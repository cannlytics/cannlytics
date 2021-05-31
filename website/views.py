"""
Views | Cannlytics Website
Created: 12/29/2020
"""
import os
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from cannlytics_website.forms import ContactForm
from utils.firebase import get_document, get_collection
from utils.mixins import BaseMixin, TemplateView
from utils.utils import get_markdown

from .decorators import check_recaptcha
from .state import lab_state, page_data, page_docs

APP = "cannlytics_website"
FILE_PATH = os.path.dirname(os.path.realpath(__file__))


class GeneralView(BaseMixin, TemplateView):
    """Generic view for most pages."""

    def get_data(self, context):
        """
        Get all data for a page from Firestore.
        """
        if context["section"]:
            data = page_data.get(context["section"])
        else:
            data = page_data.get(context["page"])
        if data is None:
            return context
        documents = data.get("documents")
        collections = data.get("collections")
        if documents:
            for item in documents:
                context[item["name"]] = get_document(item["ref"])
        if collections:
            for item in collections:
                context[item["name"]] = get_collection(
                    item["ref"],
                    limit=item.get("limit"),
                    order_by=item.get("order_by"),
                    desc=item.get("desc"),
                    filters=item.get("filters"),
                )
        return context

    def get_docs(self, context):
        """
        Get the text documents for a given page.
        """
        docs = page_docs.get(context["page"])
        if docs:
            for doc in docs:
                name = doc.replace("-", "_")
                context = get_markdown(
                    self.request, context, APP, FILE_PATH, doc, name=name
                )
        return context

    def get_context_data(self, **kwargs):
        """
        Get the context for a page.
        """
        context = super().get_context_data(**kwargs)
        context = self.get_data(context)
        context = self.get_docs(context)
        return context


class CommunityView(BaseMixin, TemplateView):
    """Community page."""

    def get_template_names(self):
        return [f"{APP}/pages/community/community.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        credentials = get_document("admin/google")
        api_key = credentials["public_maps_api_key"]
        context["api_key"] = [api_key]
        return context


class ContactView(BaseMixin, FormView):
    """Form view for contact."""

    form_class = ContactForm
    success_url = "/contact/thank-you/"

    def get_template_names(self):
        return [f"{APP}/pages/contact/contact.html"]

    # @method_decorator(check_recaptcha)
    def form_valid(self, form):
        """Submit the contact form."""
        # if self.request.recaptcha_is_valid:
        form.send_email()
        return super(ContactView, self).form_valid(form)


class LabView(BaseMixin, TemplateView):
    """View for lab detail pages."""

    def get_template_names(self):
        return [f"{APP}/pages/community/labs/lab.html"]

    def get_lab_data(self, context):
        """
        Get a lab's data from Firestore.
        """
        slug = self.kwargs.get("lab")
        filters = [{"key": "slug", "operation": "==", "value": slug}]
        labs = get_collection("labs", filters=filters)
        if labs:
            context["lab"] = labs[0]
        else:
            context["lab"] = {}
        return context

    def get_context_data(self, **kwargs):
        """Get the context for a page."""
        context = super().get_context_data(**kwargs)
        context = self.get_lab_data(context)
        context["fields"] = lab_state["detail_fields"]
        context["tabs"] = lab_state["tabs"]
        # Optional: Return JSON
        # if self.request.path.endswith('.json'):
        #     data = json.dumps(context["lab"])
        #     return HttpResponse(data, content_type="application/json")
        # else:
        return context


class NewLabView(BaseMixin, TemplateView):
    """View for adding a lab."""

    def get_template_names(self):
        return [f"{APP}/pages/community/labs/new.html"]

    def get_context_data(self, **kwargs):
        """Get the context for a page."""
        context = super().get_context_data(**kwargs)
        context["fields"] = lab_state["detail_fields"]
        context["tabs"] = lab_state["tabs"][:2]
        return context
