import React from 'react';
import ErrorModal from '../ErrorModal';

function DoubleBookingModal(props) {
    return (
        <ErrorModal
            closeModal={props.closeModal}
        >
            <text className="ResponseModal-modal-text">
                You already have a scrim posted for this time.<br/>
                Please wait for another team to post a scrim at this time.
            </text>
        </ErrorModal>
    );
}

export default DoubleBookingModal;
