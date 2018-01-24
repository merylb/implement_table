"""billingapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.views.generic.base import TemplateView, RedirectView

from implement_table.invoicing.views import InvoiceViewSet, FeesNoteViewSet
from implement_table.payment.views import PaymentViewSet
from implement_table.pec.views import CareRequestViewSet
from implement_table.table.views import TableConfigViewSet, TableConfig2ViewSet, TableFilterViewSet, \
    TableViewForColumns, TableViewSet

urlpatterns = [
                  url(r'^implement-table/.*$', TemplateView.as_view(template_name='index.html'), name='index'),
                  url(r'^$', RedirectView.as_view(url='implement-table/', permanent=False), name='redirect_to_index'),

                  url(r'^api/payment', include(PaymentViewSet.urls())),
                  url(r'^api/invoice', include(InvoiceViewSet.urls())),
                  url(r'^api/fees-note', include(FeesNoteViewSet.urls())),
                  url(r'^api/pec', include(CareRequestViewSet.urls())),
                  url(r'^api/table-config', include(TableConfigViewSet.urls())),
                  url(r'^api/table-config2', include(TableConfig2ViewSet.urls())),
                  url(r'^api/table-filter', include(TableFilterViewSet.urls())),
                  url(r'^api/table-view-cols', include(TableViewForColumns.urls())),
                  url(r'^api/table-view', include(TableViewSet.urls())),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
