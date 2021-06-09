import React from 'react';
import { Button} from '@material-ui/core';

import EventNoteIcon from '@material-ui/icons/EventNote';

function SuccessModal(props) {
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
                endIcon={<EventNoteIcon/>}
            >
                Schedule Another
            </Button>
        </React.Fragment>
    );
}

export default SuccessModal;