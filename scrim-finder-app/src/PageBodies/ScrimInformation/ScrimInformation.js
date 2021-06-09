import React, {Component} from 'react';
import Body from './Body';
import Fade from '@material-ui/core/Fade';
import Header from './Header';
import MapSelector from './MapSelector';
import { Button, CircularProgress, Modal} from '@material-ui/core';
import ResponseModal from './ResponseModal';

// Icons
import SearchIcon from '@material-ui/icons/Search';

import './ScrimInformation.css';

class ScrimInformation extends Component {

    constructor(props) {
        super(props);

        const now = new Date(new Date().toLocaleString("en-US", {timeZone: "America/New_York"}))
        const hours = now.getMinutes() >= 45 ? now.getHours() + 1 : now.getHours();
        const minutes = now.getMinutes() <= 15 || now.getMinutes() >= 45 ? 0 : 30;
        const played_at = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate(), hours, minutes);

        this.state = {
            team_name: "",
            played_at,
            team_contact: "",
            scrim_type: "",
            maps: [],
            modalVisible: false,
            modalContent: undefined,
            errors: {
                "Team Name": null,
                "Scrim Type": null,
                "Played At": null,
                "Team Contact": null,
                "Maps": null
            }
        };
    }

    closeModal = () => {
        this.setState({modalVisible: false, modalContent: undefined});
    }

    displayModal = () => {
        this.setState({modalVisible: true});
    }

    setModalContent = (jsk) => {
        this.setState({modalContent: jsk});
    }

    onTeamNameChanged = (update) => {
        const new_name = update.target.value;
        
        const errors = this.state.errors;
        errors["Team Name"] = null;
        this.setState({team_name: new_name, errors});
    }

    onTeamContactChanged = (update) => {
        const new_name = update.target.value;

        const errors = this.state.errors;
        errors["Team Contact"] = null;
        this.setState({team_contact: new_name, errors});
    }

    onScrimTypeChanged = (update) => {
        const new_scrim_type = update.target.value;

        const errors = this.state.errors;
        errors["Scrim Type"] = null
        this.setState({scrim_type: new_scrim_type, errors});
    }

    onMapsChanged = (update) => {
        const new_maps = update;

        const errors = this.state.errors;
        errors["Maps"] = null;
        this.setState({maps: new_maps, errors});
    }

    onPlayedAtChanged = (update) => {
        const hours = update.getMinutes() >= 45 ? update.getHours() + 1 : update.getHours();
        const minutes = update.getMinutes() <= 15 || update.getMinutes() >= 45 ? 0 : 30;
        const played_at = Date.UTC(update.getFullYear(), update.getMonth(), update.getDate(), hours, minutes);

        const errors = this.state.errors;
        errors["Played At"] = null;
        this.setState({played_at, errors});
    }

    validate = () => {
        const team_name_valid = this.validate_team_name();
        const scrim_type_valid = this.validate_scrim_type();
        const played_at_valid = this.validate_played_at();
        const team_contact_valid = this.validate_team_contact();
        const maps_valid = this.validate_maps();

       return team_name_valid && scrim_type_valid && played_at_valid && team_contact_valid && maps_valid;
    }

    validate_maps = () => {
        const errors = this.state.errors;
        errors["Maps"] = null;

        if (this.state.maps.length === 0) {
            errors["Maps"] = "Please select at least 1 map.";
        }

        this.setState({errors});
        return !errors["Maps"]
    }

    validate_played_at = () => {
        const errors = this.state.errors;
        errors["Played At"] = null;

        const now = new Date(new Date().toLocaleString("en-US", {timeZone: "America/New_York"}))
        now.setHours(now.getHours() - 1);
        now.setMinutes(now.getMinutes() - 30);
        const minDate = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), now.getMinutes());

        console.log(minDate);
        console.log(this.state.played_at);
        if (this.state.played_at < minDate) {
            errors["Played At"] = "Please select a time closer to the present.";
        }

        this.setState({errors});
        return !errors["Played At"];
    }

    validate_scrim_type = () => {
        const errors = this.state.errors;
        errors["Scrim Type"] = null;

        if (this.state.scrim_type !== "gameday" && this.state.scrim_type !== "6-6" && this.state.scrim_type !== "no preference") {
            errors["Scrim Type"] = "Please select a scrim type.";
        }

        this.setState({errors});
        return !errors["Scrim Type"];
    }

    validate_team_contact = () => {
        const errors = this.state.errors;
        errors["Team Contact"] = null;

        if (this.state.team_contact.length > 37) {
            errors["Team Contact"] = "Team contact cannot be more than 37 characters.";
        } else if (this.state.team_contact.length <= 5) {
            errors["Team Contact"] = "Team contact must be more than 5 characters.";
        }

        this.setState({errors});
        return !errors["Team Contact"];
    }

    validate_team_name = () => {
        const errors = this.state.errors;
        errors["Team Name"] = null;
        
        if (this.state.team_name.length >= 30) {
            errors["Team Name"] = "Team name cannot be more than 30 characters.";
        } else if (this.state.team_name.length <= 1) {
            errors["Team Name"] = "Team name must be at least 2 characters.";
        }

        this.setState({errors});
        return !errors["Team Name"] // null -> True, String -> False.
    }

    handleSubmit = () => {      
        if (!this.validate()) {
            return;
        }

        this.displayModal();

        try {
            fetch("http://localhost:5000/scrim_request", {
                method: "POST",
                headers: {
                  'Accept': 'application/json',
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "team_name": this.state.team_name,
                    "scrim_type": this.state.scrim_type,
                    "played_at": this.state.played_at,
                    "team_contact": this.state.team_contact,
                    "maps": this.state.maps
                })
            })
            .then(response => response.json())
            .then(data => this.setModalContent(
                <ResponseModal
                    response={data}
                    closeModal={this.closeModal}
                />
            ))
            .catch(error => this.setModalContent(
                <ResponseModal
                    response={error}
                    closeModal={this.closeModal}
                />
            ));

        } catch (err) {
            this.setModalContent(
                <ResponseModal
                    response={undefined}
                    closeModal={this.closeModal}
                />
            );
        }
    }

    render() {
        // There **MUST** be a better way, but I've been fighting
        // this for 4 hours and this works.
        const displayedDate = new Date(this.state.played_at);
        displayedDate.setFullYear(displayedDate.getUTCFullYear());
        displayedDate.setMonth(displayedDate.getUTCMonth());
        displayedDate.setDate(displayedDate.getUTCDate());
        displayedDate.setHours(displayedDate.getUTCHours());
        displayedDate.setMinutes(displayedDate.getUTCMinutes());

        const modalContent = this.state.modalContent !== undefined ? this.state.modalContent : (
            <div className="Scrim-information-modal-spinner-box">
                <CircularProgress size="8rem" thickness={1}/>
            </div>    
        );

        return (
            <div className="Scrim-information">
                <Modal
                    className="Scrim-information-modal"
                    open={this.state.modalVisible}
                    closeAfterTransition={true}
                    onClose={() => {}} // Only let modal content close the modal.
                >
                    <Fade in={this.state.modalVisible}>
                        <div className="Scrim-information-modal-border">
                            <div className="Scrim-information-modal-box">
                                    {modalContent}
                            </div>
                        </div>
                    </Fade>
                </Modal>
                <Header/>
                <Body
                    onTeamNameChanged={this.onTeamNameChanged}
                    onScrimTypeChanged={this.onScrimTypeChanged}
                    onPlayedAtChanged={this.onPlayedAtChanged}
                    onTeamContactChanged={this.onTeamContactChanged}
                    displayedDate={displayedDate}
                    errors={this.state.errors}
                />
                <MapSelector onMapsChanged={this.onMapsChanged} error={this.state.errors["Maps"]}/>
                <div className="Scrim-information-button-box">
                    <Button
                        variant="outlined"
                        color="secondary"
                        onClick={this.handleSubmit}
                        endIcon={<SearchIcon/>}
                    >
                        Search
                    </Button>
                </div>
            </div>
        );
    }
}

export default ScrimInformation;
