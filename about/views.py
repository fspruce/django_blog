from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib import messages
from email.mime.image import MIMEImage
import os
from .models import About
from .forms import CollaborateForm

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
    from_email = None  # Uses DEFAULT_FROM_EMAIL
    to = [email]
    # Plain text version (fallback)
    text_content = f"""
      Hi, {name}!

      Thank you for getting in touch with the site regarding a collaboration!

      I will read through your email as soon as I can, and will let you know how
      I feel about your request. This usually takes me about 2 days, so in the
      meantime, why don't you check out the site and see what else we have to offer?

      Feel free to leave a comment on the blog posts, and enjoy your time here at
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
    img_dir = 'static\\images'
    image = 'default.jpg'
    file_path = os.path.join(img_dir, image)
    with open(file_path, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-ID', '<{name}>'.format(name=image))
        img.add_header('Content-Disposition', 'inline', filename=image)
    msg.attach(img)
    msg.send()

    # Notify Owner
    subject = f"Code|Star - New Collaboration Request Recieved! | {title}"
    from_email = None  # Uses DEFAULT_FROM_EMAIL
    owner_email = os.environ.get('DEFAULT_FROM_EMAIL')
    to = [owner_email]
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
    msg.send()
