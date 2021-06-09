import React from 'react';
import ErrorModal from '../ErrorModal';

function PendingProposalModal(props) {
    return (
        <ErrorModal
            closeModal={props.closeModal}
        >
            <text className="ResponseModal-modal-text">
                A team is already attempting to book a scrim with you at this time.<br/>
                Please check your DMs.
            </text>
        </ErrorModal>
    );
}

export default PendingProposalModal;
