import React from 'react';

import SuccessModal from '../SuccessModal';

function ScrimFoundModal(props){
    return <SuccessModal
                closeModal={props.closeModal}
            >
                <text className="ResponseModal-modal-text">
                    Found a matching scrim! The bot will message you shortly with more information.
                </text>
            </SuccessModal>
}

export default ScrimFoundModal;