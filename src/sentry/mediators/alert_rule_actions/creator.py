from sentry.mediators import Mediator, Param, external_requests
from sentry.utils.cache import memoize


class AlertRuleActionCreator(Mediator):
    install = Param("sentry.models.SentryAppInstallation")
    fields = Param(object)
    uri = Param((str,))
    alert_rule_trigger_action = Param("sentry.models.AlertRuleTriggerAction")

    def call(self):
        self._make_external_request()
        self._save_alert_rule_action()
        return self.response

    def _save_alert_rule_action(self):
        self.alert_rule_trigger_action.save()

    def _make_external_request(self):
        self.response = external_requests.AlerRuleActionRequester.run(
            install=self.install,
            uri=self.uri,
            fields=self.fields,
        )

    @memoize
    def sentry_app(self):
        return self.install.sentry_app
