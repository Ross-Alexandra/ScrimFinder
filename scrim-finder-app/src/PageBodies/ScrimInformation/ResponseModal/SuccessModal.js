import React from 'react';
import { Button} from '@material-ui/core';

import EventNoteIcon from '@material-ui/icons/EventNote';

function SuccessModal(props) {
    return (
        <React.Fragment>
            {props.message}
            <Button
                variant="outlined"
                color="secondary"
                onClick={props.closeModal}
                endIcon={<EventNoteIcon/>}
            >
                Schedule Another
            </Button>
        </React.Fragment>
    );
}

export default SuccessModal;