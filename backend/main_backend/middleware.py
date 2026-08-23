class CloudinaryCSPMiddleware:
    """
    Inject a Content-Security-Policy header that permits images served from
    Cloudinary's CDN (res.cloudinary.com) to be displayed in Django admin.

    Without this, when DEBUG=False Django's SecurityMiddleware sends a default
    CSP that blocks any external image domain, causing Cloudinary thumbnails
    to appear blank/broken even though the URLs are correct.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only inject for admin pages (no need to loosen CSP site-wide)
        if request.path.startswith('/admin'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
                "    https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
                "    https://fonts.googleapis.com; "
                "style-src 'self' 'unsafe-inline' "
                "    https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
                "    https://fonts.googleapis.com; "
                "font-src 'self' "
                "    https://fonts.googleapis.com https://fonts.gstatic.com "
                "    https://cdnjs.cloudflare.com; "
                "img-src 'self' data: blob: "
                "    https://res.cloudinary.com "   # ← Cloudinary image CDN
                "    https://cdn.jsdelivr.net; "
                "connect-src 'self';"
            )

        return response
