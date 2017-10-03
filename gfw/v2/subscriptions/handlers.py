# Global Forest Watch API
# Copyright (C) 2013 World Resource Institute
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import json
import webapp2

from gfw.middlewares.user import UserAuthMiddleware
from gfw.models.subscription import Subscription
from gfw.common import gfw_url
from gfw.lib.subscription_overview_service import SubscriptionOverviewService

class SubscriptionsApi(UserAuthMiddleware):
    routes_without_authorisation = [
        'overview'
    ]

    def index(self):
        subscriptions = Subscription.query(Subscription.user_id==self.user.key).fetch()
        subscriptions = [s.to_dict() for s in subscriptions]
        self.complete('respond', subscriptions)

    def create(self):
        subscription = Subscription.subscribe(self.__get_params(), self.user)

        if subscription:
            token = subscription.key.urlsafe()
            self.response.set_status(201)
            self.complete('respond', {"subscribe": True, "key": token})
        else:
            self.write_error(400, 'Bad Request')

    def send_confirmation(self, subscription_id):
        subscription = Subscription.get_by_id(int(subscription_id))

        if subscription:
            subscription.unconfirm();
            self.redirect(gfw_url('my_gfw/subscriptions',
                {'subscription_confirmation_sent': 'true'}))
        else:
            self.write_error(404, 'Not Found')

    def confirm(self, subscription_id):
        if Subscription.confirm_by_id(subscription_id):
            self.redirect(gfw_url('my_gfw/subscriptions',
                {'subscription_confirmed': 'true'}))
        else:
            self.write_error(404, 'Not Found')

    def unsubscribe(self, subscription_id):
        subscription = Subscription.get_by_id(int(subscription_id))

        if subscription:
            subscription.unsubscribe()
            self.redirect(gfw_url('my_gfw/subscriptions',
                {'unsubscribed': 'true'}))
        else:
            self.write_error(404, 'Not found')

    def delete(self, subscription_id):
        subscription = Subscription.get_by_id(int(subscription_id))

        if subscription:
            subscription.unsubscribe()
            self.complete('respond', subscription.to_dict())
        else:
            self.write_error(404, 'Not found')

    def put(self, subscription_id):
        subscription = Subscription.get_by_id(int(subscription_id))

        if subscription:
            subscription.populate(**self.__get_params())
            subscription.put()

            self.complete('respond', subscription.to_dict())
        else:
            self.write_error(404, 'Not found')

    def overview(self, subscription_id):
        subscription = Subscription.get_by_id(int(subscription_id))

        if subscription:
            if (not hasattr(subscription, 'overview_image')) or (subscription.overview_image is None):
                subscription.overview_image = SubscriptionOverviewService.overview_image(subscription)
                subscription.put()

            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(subscription.overview_image)
        else:
            self.write_error(404, 'Not found')

    def __get_params(self):
        accepted_params = ['name', 'topic', 'email', 'iso', 'id1',
                'ifl', 'ifl_id1', 'use', 'useid', 'pa', 'wdpaid',
                'latest', 'geom', 'url', 'namespace', 'geostore',
                'language']
        params = json.loads(self.request.body)
        return {k: v for k, v in params.items() if k in accepted_params}
