import React from 'react';
import { Button} from '@material-ui/core';

import CloseIcon from '@material-ui/icons/Close';

function ErrorModal(props) {
    return (
        <React.Fragment>
            {props.message}
            <Button
                variant="outlined"
                color="secondary"
                onClick={props.closeModal}
                endIcon={<CloseIcon/>}
            >
                Close
            </Button>
        </React.Fragment>
    );
}

export default ErrorModal;