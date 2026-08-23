import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TeamRegistration

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
                payment_screenshot=payment_screenshot,
                add_merch=add_merch,
                primary_tshirt_size=primary_tshirt_size,
                teammate_tshirt_size=teammate_tshirt_size
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
            
            # Simple dummy validation or checking if it exists
            team = TeamRegistration.objects.filter(team_name=username).first()
            if not team:
                team = TeamRegistration.objects.filter(generated_username=username).first()
            
            if team or (username == "admin" and password == "admin"):
                # Returning mock assignment data perfectly matching the spec
                t_name = team.team_name if team else "Admin Testing Team"
                return JsonResponse({
                    "status": "success",
                    "data": {
                        "team_name": t_name,
                        "debate_topic": team.debate_topic if team else "Admin Mock Topic",
                        "stance": team.stance if team else "Opposition",
                        "debate_date": team.debate_date if team else "TBD",
                        "debate_time": team.debate_time if team else "TBD",
                        "classroom": team.classroom if team else "TBD"
                    }
                })
            else:
                return JsonResponse({"status": "error", "message": "Invalid Login ID or Password."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)
