import React from 'react';

import ErrorModal from '../ErrorModal';

function UnknownErrorModal(props) {
    return <ErrorModal 
                closeModal={props.closeModal}
            >
                <text className="ResponseModal-modal-text">
                    An unknown Error has occurred, please try again later.<br/>
                    Code: {props.code}
                </text>
            </ErrorModal>
}

export default UnknownErrorModal;