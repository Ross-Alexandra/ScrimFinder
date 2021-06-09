import React, { Component } from 'react';

// Import basic modals
import {
    BadContactModal,
    DoubleBookingModal,
    NetworkErrorModal,
    PendingProposalModal,
    ScrimFoundModal,
    ScrimPostedModal,
    UnknownErrorModal
 } from './ModalTypes';


class ResponseModal extends Component {
    constructor(props) {
        super(props);

        const response = this.props.response;

        // logic to determine what type of response 
        // this is, and create the appropriate modal.
        if (response instanceof TypeError) {
            this.modal = (
                <NetworkErrorModal closeModal={this.props.closeModal}/>
            );
        } else if (response.code === 0) {
            this.modal = (
                <BadContactModal closeModal={this.props.closeModal}/>
            );
        } else if (response.code === 1 || response.code === 1001 || response.code === 1002) {
            this.modal = (
                <UnknownErrorModal closeModal={this.props.closeModal} code={response.code}/>
            );
        } else if (response.code === 2) {
            this.modal = (
                <DoubleBookingModal closeModal={this.props.closeModal}/>
            );
        } else if (response.code === 3) {
            this.modal = (
                <PendingProposalModal closeModal={this.props.closeModal}/>
            );
        } else if (response.code === 1003) {
            this.modal = (
                <ScrimPostedModal closeModal={this.props.closeModal}/>
            );
        } else if (response.code === 1004) {
            this.modal = (
                <ScrimFoundModal closeModal={this.props.closeModal}/>
            );
        }
        else {
            this.modal = (
                <UnknownErrorModal closeModal={this.props.closeModal} code={-1}/>
            );
        }
    }

    render() {
        return (
            <React.Fragment>
                {this.modal}
            </React.Fragment>
        );
    }
}

export default ResponseModal;