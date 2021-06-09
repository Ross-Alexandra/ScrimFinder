import React from 'react';

import ErrorModal from '../ErrorModal';

function NetworkErrorModal(props) {
    return <ErrorModal
                closeModal={props.closeModal}
            >
                <text className="ResponseModal-modal-text">
                    A network error occurred. Please try again later.
                </text>
            </ErrorModal>
}

export default NetworkErrorModal;