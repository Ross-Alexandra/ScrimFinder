import React, { Component } from 'react';

// Import basic modals
import NetworkErrorModal from './NetworkError';
import ScrimFoundModal from './ScrimFound';
import ScrimPostedModal from './ScrimPosted';
import UnknownErrorModal from './UnknownError';


class ResponseModal extends Component {
    constructor(props) {
        super(props);

        const response = this.props.response;
        console.log(response);

        // logic to determine what type of response 
        // this is, and create the appropriate modal.
        if (response instanceof TypeError) {
            this.modal = (
                <NetworkErrorModal closeModal={this.props.closeModal}/>
            );
        } // TODO: Add further logical switches here.
        else {
            this.modal = (
                <UnknownErrorModal closeModal={this.props.closeModal}/>
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