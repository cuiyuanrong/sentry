import React from 'react';
import {RouteComponentProps} from 'react-router';

import {addErrorMessage} from 'app/actionCreators/indicator';
import {updateOrganization} from 'app/actionCreators/organizations';
import SentryDocumentTitle from 'app/components/sentryDocumentTitle';
import organizationSecurityAndPrivacyGroups from 'app/data/forms/organizationSecurityAndPrivacyGroups';
import {t} from 'app/locale';
import {Organization} from 'app/types';
import withOrganization from 'app/utils/withOrganization';
import AsyncView from 'app/views/asyncView';
import Form from 'app/views/settings/components/forms/form';
import JsonForm from 'app/views/settings/components/forms/jsonForm';
import SettingsPageHeader from 'app/views/settings/components/settingsPageHeader';

import DataScrubbing from '../components/dataScrubbing';

type Props = RouteComponentProps<{orgId: string; projectId: string}, {}> & {
  organization: Organization;
};

class OrganizationSecurityAndPrivacyContent extends AsyncView<Props> {
  getEndpoints(): ReturnType<AsyncView['getEndpoints']> {
    const {orgId} = this.props.params;
    return [['authProvider', `/organizations/${orgId}/auth-provider/`]];
  }

  handleUpdateOrganization = (data: Organization) => {
    // This will update OrganizationStore (as well as OrganizationsStore
    // which is slightly incorrect because it has summaries vs a detailed org)
    updateOrganization(data);
  };

  renderBody() {
    const {organization} = this.props;
    const {orgId} = this.props.params;
    const initialData = organization;
    const endpoint = `/organizations/${orgId}/`;
    const access = new Set(organization.access);
    const features = new Set(organization.features);
    const relayPiiConfig = organization.relayPiiConfig;
    const {authProvider} = this.state;
    const title = t('Security & Privacy');

    return (
      <React.Fragment>
        <SentryDocumentTitle title={title} orgSlug={organization.slug} />
        <SettingsPageHeader title={title} />
        <Form
          data-test-id="organization-settings-security-and-privacy"
          apiMethod="PUT"
          apiEndpoint={endpoint}
          initialData={initialData}
          additionalFieldProps={{hasSsoEnabled: !!authProvider}}
          onSubmitSuccess={this.handleUpdateOrganization}
          onSubmitError={() => addErrorMessage(t('Unable to save change'))}
          saveOnBlur
          allowUndo
        >
          <JsonForm
            features={features}
            forms={organizationSecurityAndPrivacyGroups}
            disabled={!access.has('org:write')}
          />
        </Form>
        <DataScrubbing
          additionalContext={t('These rules can be configured for each project.')}
          endpoint={endpoint}
          relayPiiConfig={relayPiiConfig}
          disabled={!access.has('org:write')}
          organization={organization}
          onSubmitSuccess={this.handleUpdateOrganization}
        />
      </React.Fragment>
    );
  }
}

export default withOrganization(OrganizationSecurityAndPrivacyContent);
