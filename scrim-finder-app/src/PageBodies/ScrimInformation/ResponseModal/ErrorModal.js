import React from 'react';
import { Button} from '@material-ui/core';

import CloseIcon from '@material-ui/icons/Close';

function ErrorModal(props) {
    return (
        <React.Fragment>
            <div className="ResponseModal-content-box">
                {props.children}
            </div>
            <Button
                variant="outlined"
                color="secondary"
                style={{
                    marginTop: "auto",
                    marginBottom: "20px"
                }}
                onClick={props.closeModal}
                endIcon={<CloseIcon/>}
            >
                Close
            </Button>
        </React.Fragment>
    );
}

export default ErrorModal;