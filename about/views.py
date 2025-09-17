from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib import messages
from email.mime.image import MIMEImage
from django.conf import settings
from django.contrib.staticfiles.finders import find
import logging
import os
from .models import About
from .forms import CollaborateForm

logger = logging.getLogger(__name__)

# Create your views here.


def about_me(request):
    """
    Renders the most recent information on the website author and allows
    user colaboration requests.
    Displays an individual instance of :model:`about.About`.
    **Context**
    ``about``
        The most recent instance of :model:`about.About`.
    ``collaborate_form``
        An instance of :form:`about.CollaborateForm`.
    **Template**
        :template:`about/about.html`.
    """

    if request.method == "POST":
        collaborate_form = CollaborateForm(data=request.POST)
        if collaborate_form.is_valid():
            name = collaborate_form.cleaned_data['name']
            email = collaborate_form.cleaned_data['email']
            title = collaborate_form.cleaned_data['title']
            message = collaborate_form.cleaned_data['message']
            collaboration_email(name, email, title, message, request)
            collaborate_form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                (
                    "Collaboration request recieved! "
                    "I endeavour to respond within 2 working days."
                ),
            )

    about = About.objects.all().order_by("-updated_on").first()
    collaborate_form = CollaborateForm()

    return render(
        request,
        "about/about.html",
        {
            "about": about,
            "collaborate_form": collaborate_form,
        },
    )


def collaboration_email(name, email, title, message, request=None):
    # Thank User
    subject = f"Code|Star - Thank you for your request! | {title}"
    # Prefer the Django setting for DEFAULT_FROM_EMAIL; fall back to env
    # or a safe default
    from_email = (
        getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        or os.environ.get('DEFAULT_FROM_EMAIL')
        or 'no-reply@example.com'
    )
    to = [email]
    # Plain text version (fallback)
    text_content = f"""
      Hi, {name}!

      Thank you for getting in touch with the site regarding a collaboration!

    I will read through your email as soon as I can, and will let you know
    how
      I feel about your request. This usually takes me about 2 days, so in the
    meantime, why don't you check out the site and see what else we have to
    offer?

    Feel free to leave a comment on the blog posts, and enjoy your time here
    at
      Code|Star!

      Cheers,
      The Code|Star Team.
      _______________________________________________________________________________
      From {name}:
      Title: {title}
      Message:
            {message}
    """

    # HTML version
    html_content = render_to_string(
        'emails/user_notify.html',
        {
            'name': name,
            'title': title,
            'message': message,
        },
    )
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.mixed_subtype = 'related'
    msg.attach_alternative(html_content, "text/html")
    # Locate static image in a portable way (works on Heroku/Linux and locally)
    image = 'images/default.jpg'
    file_path = find(image)
    if file_path:
        try:
            with open(file_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header(
                    'Content-ID',
                    '<{name}>'.format(name=os.path.basename(file_path)),
                )
                img.add_header(
                    'Content-Disposition', 'inline',
                    filename=os.path.basename(file_path),
                )
                msg.attach(img)
        except Exception:
            logger.exception('Failed to attach image %s', file_path)
    else:
        logger.debug(
            'Static image not found: %s. Sending without inline image.', image
        )

    try:
        msg.send()
    except Exception:
        logger.exception('Failed to send thank-you email to %s', to)
        if request:
            messages.error(
                request,
                'There was an error sending the confirmation email. '
                'Please try again later.',
            )

    # Notify Owner
    subject = f"Code|Star - New Collaboration Request Recieved! | {title}"
    from_email = (
        getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        or os.environ.get('DEFAULT_FROM_EMAIL')
        or 'no-reply@example.com'
    )
    owner_email = (
        getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        or os.environ.get('DEFAULT_FROM_EMAIL')
    )
    to = [owner_email] if owner_email else []
    # Plain text version (fallback)
    text_content = f"""
      Collaboration Request Recieved!

      From: {name} ({email})
      Title: {title}
      Message:
            {message}
      _______________________________________________________________________________
      Email sent via Code|Star
      _______________________________________________________________________________
    """

    # HTML version
    html_content = render_to_string(
        'emails/owner_notify.html',
        {
            'name': name,
            'title': title,
            'message': message,
            'email': email,
        },
    )
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    try:
        if to:
            msg.send()
        else:
            logger.warning(
                'Owner email not configured; owner notification not sent.'
            )
    except Exception:
        logger.exception('Failed to send owner notification email to %s', to)
        if request:
            messages.error(
                request,
                'There was an error sending the site owner '
                'notification email.',
            )
