import React from 'react';

import ErrorModal from './ErrorModal';

function NetworkErrorModal(props) {
    return <ErrorModal
                message={"A network error occurred. Please try again later."}
                closeModal={props.closeModal}
            />
}

export default NetworkErrorModal;