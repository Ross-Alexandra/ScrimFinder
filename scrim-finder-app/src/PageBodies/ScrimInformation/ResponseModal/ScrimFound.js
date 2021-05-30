import React from 'react';

import SuccessModal from './SuccessModal';

function ScrimFoundModal(props){
    return <SuccessModal
                message="Found a matching scrim! The bot will message you shortly with more information."
                closeModal={props.closeModal}
            />
}

export default ScrimFoundModal;