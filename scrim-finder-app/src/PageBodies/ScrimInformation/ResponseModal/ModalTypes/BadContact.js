import React from 'react';
import ErrorModal from '../ErrorModal';

import './modals.css';

function BadContactModal(props) {
    return (
        <ErrorModal
            closeModal={props.closeModal}
        >
            <text className="ResponseModal-modal-text">You must be a member of the NASC discord to post a scrim</text>
            <iframe
                title="NASC Discord"
                src="https://discord.com/widget?id=837031378910576721&theme=dark"
                width="350"
                height="500"
                allowtransparency="true"
                frameborder="0"
                sandbox="allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"/>
        </ErrorModal>
    );
}

export default BadContactModal;