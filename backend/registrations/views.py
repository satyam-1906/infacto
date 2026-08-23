import json
import hmac
import hashlib
import time
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import TeamRegistration
import cloudinary
import cloudinary.uploader

# ── Simple token helpers (no session cookies needed across origins) ──────────
ADMIN_TOKEN_SALT = 'infacto-admin-token-v1'

def _generate_admin_token(username: str) -> str:
    """Return a signed token embedding username and timestamp."""
    ts = str(int(time.time()))
    payload = f"{username}:{ts}"
    secret = (settings.SECRET_KEY + ADMIN_TOKEN_SALT).encode()
    sig = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"

def _verify_admin_token(token: str, max_age_seconds: int = 86400) -> bool:
    """Return True if the token is valid and not expired (default 24 h)."""
    try:
        parts = token.split(':')
        if len(parts) != 3:
            return False
        username, ts, sig = parts
        # Verify signature
        payload = f"{username}:{ts}"
        secret = (settings.SECRET_KEY + ADMIN_TOKEN_SALT).encode()
        expected = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return False
        # Verify age
        if int(time.time()) - int(ts) > max_age_seconds:
            return False
        return True
    except Exception:
        return False

@csrf_exempt
def submit_registration(request):
    if request.method == 'POST':
        try:
            # Extract standard text fields
            primary_name = request.POST.get('primary_name')
            teammate_name = request.POST.get('teammate_name', '')
            primary_email = request.POST.get('primary_email')
            teammate_email = request.POST.get('teammate_email', '')
            primary_mobile = request.POST.get('primary_mobile')
            teammate_mobile = request.POST.get('teammate_mobile', '')
            team_name = request.POST.get('team_name')
            institution = request.POST.get('institution')
            experience = request.POST.get('experience', '')
            referral_code = request.POST.get('referral_code', '')
            
            # Merch Hooks
            add_merch = request.POST.get('add_merch') == 'on' or request.POST.get('add_merch') == 'true'
            primary_tshirt_size = request.POST.get('primary_tshirt_size', '')
            teammate_tshirt_size = request.POST.get('teammate_tshirt_size', '')
            
            # Extract the uploaded screenshot file
            payment_screenshot = request.FILES.get('payment_screenshot')

            if not all([primary_name, primary_email, primary_mobile, team_name, institution, payment_screenshot]):
                return JsonResponse({"status": "error", "message": "Missing required fields!"}, status=400)

            if TeamRegistration.objects.filter(team_name__iexact=team_name).exists():
                return JsonResponse({"status": "error", "message": "A team with this Team Name already exists! Please choose another."}, status=400)

            # ── Upload payment screenshot to Cloudinary ──────────────────────
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True,
            )

            # Build a base64 data URI so Cloudinary receives the MIME type
            # explicitly — the most reliable upload method, immune to filename
            # issues, file-pointer positions, or format-detection failures.
            payment_screenshot.seek(0)
            raw_bytes = payment_screenshot.read()
            mime_type = payment_screenshot.content_type or 'image/jpeg'
            b64_data = base64.b64encode(raw_bytes).decode('utf-8')
            data_uri = f"data:{mime_type};base64,{b64_data}"

            upload_result = cloudinary.uploader.upload(
                data_uri,
                folder='infacto/payment_screenshots',
                resource_type='image',
            )
            cloudinary_url = upload_result.get('secure_url', '')
            if not cloudinary_url:
                return JsonResponse({"status": "error", "message": "Image upload to Cloudinary failed."}, status=500)
            # ────────────────────────────────────────────────────────────────

            # Create Record
            TeamRegistration.objects.create(
                primary_name=primary_name,
                teammate_name=teammate_name,
                primary_email=primary_email,
                teammate_email=teammate_email,
                primary_mobile=primary_mobile,
                teammate_mobile=teammate_mobile,
                team_name=team_name,
                institution=institution,
                experience=experience,
                payment_screenshot=cloudinary_url,
                add_merch=add_merch,
                primary_tshirt_size=primary_tshirt_size,
                teammate_tshirt_size=teammate_tshirt_size,
                referral_code=referral_code
            )
            
            return JsonResponse({"status": "success", "message": "Registration received!"})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)


@csrf_exempt
def candidate_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()

            if not username or not password:
                return JsonResponse({"status": "error", "message": "Username and password are required."}, status=400)

            from django.contrib.auth import authenticate, login
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)  # Create session (for Django admin panel)

                if user.is_staff or user.is_superuser:
                    token = _generate_admin_token(user.username)
                    return JsonResponse({
                        "status": "success",
                        "is_admin": True,
                        "admin_token": token,
                        "data": {
                            "team_name": "Administrator"
                        }
                    })

                # Lookup the team linked to this generated_username
                team = TeamRegistration.objects.filter(generated_username=username).first()
                return JsonResponse({
                    "status": "success",
                    "is_admin": False,
                    "data": {
                        "team_name": team.team_name if team else username,
                        "debate_topic": team.debate_topic if team else "TBD",
                        "stance": team.stance if team else "TBD",
                        "debate_date": team.debate_date if team else "TBD",
                        "debate_time": team.debate_time if team else "TBD",
                        "classroom": team.classroom if team else "TBD"
                    }
                })
            else:
                return JsonResponse({"status": "error", "message": "Invalid Login ID or Password."}, status=401)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)


@csrf_exempt
def get_all_registrations(request):
    token = request.headers.get('X-Admin-Token', '')
    if not token or not _verify_admin_token(token):
        # Fallback: also accept session-based auth (for same-origin use)
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

    try:
        regs = TeamRegistration.objects.all().order_by('id')
        data = []
        for r in regs:
            data.append({
                "id": r.id,
                "team_name": r.team_name,
                "primary_name": r.primary_name,
                "primary_email": r.primary_email,
                "primary_mobile": r.primary_mobile,
                "teammate_name": r.teammate_name,
                "teammate_email": r.teammate_email,
                "teammate_mobile": r.teammate_mobile,
                "institution": r.institution,
                "experience": r.experience,
                "payment_screenshot_url": r.payment_screenshot or "",
                "add_merch": r.add_merch,
                "primary_tshirt_size": r.primary_tshirt_size,
                "teammate_tshirt_size": r.teammate_tshirt_size,
                "debate_topic": r.debate_topic,
                "stance": r.stance,
                "debate_date": r.debate_date,
                "debate_time": r.debate_time,
                "classroom": r.classroom,
                "is_approved": r.is_approved,
                "generated_username": r.generated_username,
                "referral_code": r.referral_code or ""
            })
        return JsonResponse({"status": "success", "data": data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def toggle_approval(request):
    token = request.headers.get('X-Admin-Token', '')
    if not token or not _verify_admin_token(token):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            reg_id = body.get('id')
            reg = TeamRegistration.objects.get(id=reg_id)

            reg.is_approved = not reg.is_approved
            reg.save()

            return JsonResponse({
                "status": "success",
                "message": f"Successfully toggled approval for team {reg.team_name}.",
                "is_approved": reg.is_approved
            })
        except TeamRegistration.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Registration not found."}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)


@csrf_exempt
def health_check(request):
    """
    Simple health check API endpoint used by the keepalive daemon
    to prevent the server from sleeping.
    """
    return JsonResponse({"status": "healthy", "timestamp": time.time()})


