import React from 'react';

import ErrorModal from './ErrorModal';

function UnknownErrorModal(props) {
    return <ErrorModal 
                message={"An unknown Error has occurred, please try again later."}
                closeModal={props.closeModal}
            />
}

export default UnknownErrorModal;