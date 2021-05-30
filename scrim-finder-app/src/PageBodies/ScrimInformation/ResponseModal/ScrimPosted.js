import React from 'react';

import SuccessModal from './SuccessModal';

function ScrimPostedModal(props) {
    return <SuccessModal
                message={"Didn't find a matching scrim, but posted an LFS message. Good Luck!"}
                closeModal={props.closeModal}
            />
}

export default ScrimPostedModal;