from django.core.mail import send_mail, EmailMultiAlternatives
from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib import messages
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
            message = collaborate_form.cleaned_data['message']
            send_ty_email(name, email, message)
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


def send_ty_email(name, email, message):
    subject = "Code|Star - Thank you for your request!"
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
      {message}
    """

    # HTML version
    html_content = render_to_string('templates/emails/ty_email.html',
                                    {'name': name,
                                     'message': message,
                                     })
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send
