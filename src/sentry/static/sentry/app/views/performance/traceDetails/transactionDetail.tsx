import React from 'react';
import styled from '@emotion/styled';
import {Location} from 'history';
import omit from 'lodash/omit';

import Alert from 'app/components/alert';
import Button from 'app/components/button';
import DateTime from 'app/components/dateTime';
import Link from 'app/components/links/link';
import {generateIssueEventTarget} from 'app/components/quickTrace/utils';
import {PAGE_URL_PARAM} from 'app/constants/globalSelectionHeader';
import {IconChevron, IconWarning} from 'app/icons';
import {t, tn} from 'app/locale';
import space from 'app/styles/space';
import {Organization} from 'app/types';
import {generateEventSlug} from 'app/utils/discover/urls';
import getDynamicText from 'app/utils/getDynamicText';
import {TraceFullDetailed} from 'app/utils/performance/quickTrace/types';
import {WEB_VITAL_DETAILS} from 'app/utils/performance/vitals/constants';
import {transactionSummaryRouteWithQuery} from 'app/views/performance/transactionSummary/utils';
import {getTransactionDetailsUrl} from 'app/views/performance/utils';

import {
  ErrorDot,
  ErrorLevel,
  ErrorMessageContent,
  ErrorMessageTitle,
  ErrorTitle,
  Row,
  Tags,
  TransactionDetails,
  TransactionDetailsContainer,
} from './styles';

type Props = {
  location: Location;
  organization: Organization;
  transaction: TraceFullDetailed;
};

type State = {
  errorsOpened: boolean;
};

class TransactionDetail extends React.Component<Props, State> {
  state: State = {
    errorsOpened: false,
  };

  toggleErrors = () => {
    this.setState(({errorsOpened}) => ({errorsOpened: !errorsOpened}));
  };

  renderTransactionErrors() {
    const {organization, transaction} = this.props;
    const {errorsOpened} = this.state;
    const {errors} = transaction;

    if (errors.length === 0) {
      return null;
    }

    return (
      <Alert system type="error" icon={<IconWarning size="md" />}>
        <ErrorMessageTitle>
          {tn(
            'An error event occurred in this transaction.',
            '%s error events occurred in this transaction.',
            errors.length
          )}
          <Toggle priority="link" onClick={this.toggleErrors}>
            <IconChevron direction={errorsOpened ? 'up' : 'down'} />
          </Toggle>
        </ErrorMessageTitle>
        {errorsOpened && (
          <ErrorMessageContent>
            {errors.map(error => (
              <React.Fragment key={error.event_id}>
                <ErrorDot level={error.level} />
                <ErrorLevel>{error.level}</ErrorLevel>
                <ErrorTitle>
                  <Link to={generateIssueEventTarget(error, organization)}>
                    {error.title}
                  </Link>
                </ErrorTitle>
              </React.Fragment>
            ))}
          </ErrorMessageContent>
        )}
      </Alert>
    );
  }

  renderGoToTransactionButton() {
    const {location, organization, transaction} = this.props;

    const eventSlug = generateEventSlug({
      id: transaction.event_id,
      project: transaction.project_slug,
    });

    const target = getTransactionDetailsUrl(
      organization,
      eventSlug,
      transaction.transaction,
      omit(location.query, Object.values(PAGE_URL_PARAM))
    );

    return (
      <StyledButton size="xsmall" to={target}>
        {t('View Transaction')}
      </StyledButton>
    );
  }

  renderGoToSummaryButton() {
    const {location, organization, transaction} = this.props;

    const target = transactionSummaryRouteWithQuery({
      orgSlug: organization.slug,
      transaction: transaction.transaction,
      query: omit(location.query, Object.values(PAGE_URL_PARAM)),
      projectID: String(transaction.project_id),
    });

    return (
      <StyledButton size="xsmall" to={target}>
        {t('View Summary')}
      </StyledButton>
    );
  }

  renderMeasurements() {
    const {transaction} = this.props;
    const {measurements = {}} = transaction;

    const measurementKeys = Object.keys(measurements)
      .filter(name => Boolean(WEB_VITAL_DETAILS[`measurements.${name}`]))
      .sort();

    if (measurementKeys.length <= 0) {
      return null;
    }

    return (
      <React.Fragment>
        {measurementKeys.map(measurement => (
          <Row
            key={measurement}
            title={WEB_VITAL_DETAILS[`measurements.${measurement}`]?.name}
          >
            {`${Number(measurements[measurement].value.toFixed(3)).toLocaleString()}ms`}
          </Row>
        ))}
      </React.Fragment>
    );
  }

  renderTransactionDetail() {
    const {location, organization, transaction} = this.props;
    const startTimestamp = Math.min(transaction.start_timestamp, transaction.timestamp);
    const endTimestamp = Math.max(transaction.start_timestamp, transaction.timestamp);
    const duration = (endTimestamp - startTimestamp) * 1000;
    const durationString = `${Number(duration.toFixed(3)).toLocaleString()}ms`;

    return (
      <TransactionDetails>
        <table className="table key-value">
          <tbody>
            <Row title="Transaction ID" extra={this.renderGoToTransactionButton()}>
              {transaction.event_id}
            </Row>
            <Row title="Transaction" extra={this.renderGoToSummaryButton()}>
              {transaction.transaction}
            </Row>
            <Row title="Transaction Status">{transaction['transaction.status']}</Row>
            <Row title="Span ID">{transaction.span_id}</Row>
            <Row title="Project">{transaction.project_slug}</Row>
            <Row title="Start Date">
              {getDynamicText({
                fixed: 'Mar 19, 2021 11:06:27 AM UTC',
                value: (
                  <React.Fragment>
                    <DateTime date={startTimestamp * 1000} />
                    {` (${startTimestamp})`}
                  </React.Fragment>
                ),
              })}
            </Row>
            <Row title="End Date">
              {getDynamicText({
                fixed: 'Mar 19, 2021 11:06:28 AM UTC',
                value: (
                  <React.Fragment>
                    <DateTime date={endTimestamp * 1000} />
                    {` (${endTimestamp})`}
                  </React.Fragment>
                ),
              })}
            </Row>
            <Row title="Duration">{durationString}</Row>
            <Row title="Operation">{transaction['transaction.op'] || ''}</Row>
            {this.renderMeasurements()}
            <Tags
              location={location}
              organization={organization}
              transaction={transaction}
            />
          </tbody>
        </table>
      </TransactionDetails>
    );
  }

  render() {
    return (
      <TransactionDetailsContainer
        onClick={event => {
          // prevent toggling the transaction detail
          event.stopPropagation();
        }}
      >
        {this.renderTransactionErrors()}
        {this.renderTransactionDetail()}
      </TransactionDetailsContainer>
    );
  }
}

const StyledButton = styled(Button)`
  position: absolute;
  top: ${space(0.75)};
  right: ${space(0.5)};
`;

const Toggle = styled(Button)`
  font-weight: bold;
  color: ${p => p.theme.subText};
  :hover {
    color: ${p => p.theme.textColor};
  }
`;

export default TransactionDetail;
