import React from 'react';

import SuccessModal from '../SuccessModal';

function ScrimPostedModal(props) {
    return <SuccessModal
                closeModal={props.closeModal}
            >
                <text className="ResponseModal-modal-text">
                    No matching scrims were found.<br/>
                    If your scrim was for today then an LFS message was posted in the NASC Discord. Otherwise it will be posted day-of.
                </text>
            </SuccessModal>
}

export default ScrimPostedModal;