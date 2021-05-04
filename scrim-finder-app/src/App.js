import React, {Component} from 'react';
import DatePicker from "react-datepicker";

import './App.css';
import "react-datepicker/dist/react-datepicker.css";


class App extends Component {

    constructor(props) {
        super(props);

        const now = new Date();
        const hours = now.getMinutes() >= 45 ? now.getHours() + 1 : now.getHours();
        const minutes = now.getMinutes() <= 15 || now.getMinutes() >= 45 ? 0 : 30;
        const played_at = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate(), hours, minutes);

        this.state = {
            team_name: "",
            played_at,
            team_contact: "",
            maps_text: "",
            maps: []
        };
    }

    onTeamNameChanged = (update) => {
        const new_name = update.target.value;

        if (new_name.length > 29) {
            // do nothing.
            return;
        }

        this.setState({team_name: new_name});
    }

    onTeamContactChanged = (update) => {
        const new_name = update.target.value;

        if (new_name.length > 36) {
            // do nothing
            return;
        }

        this.setState({team_contact: new_name});
    }

    onMapsChanged = (update) => {

        const new_maps = update.target.value;
        this.setState({
            maps_text: new_maps,
            maps: new_maps.split(",")
        });
    }

    onPlayedAtChanged = (update) => {
        const hours = update.getMinutes() >= 45 ? update.getHours() + 1 : update.getHours();
        const minutes = update.getMinutes() <= 15 || update.getMinutes() >= 45 ? 0 : 30;
        const played_at = Date.UTC(update.getFullYear(), update.getMonth(), update.getDate(), hours, minutes);

        console.log(played_at);

        this.setState({played_at});
    }

    handleSubmit = (event) => {       
        event.preventDefault();
        
        try {
            const rawResponse = fetch("http://localhost:5000/scrim_request", {
                method: "POST",
              headers: {
                  'Accept': 'application/json',
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "team_name": this.state.team_name,
                    "played_at": this.state.played_at,
                    "team_contact": this.state.team_contact,
                    "maps": this.state.maps
                })
            });
        } catch (err) {
            console.log(err);
        }
    }

    render() {
        console.log("Rendering");
        
        // There **MUST** be a better way, but I've been fighting
        // this for 4 hours and this works.
        const displayedDate = new Date(this.state.played_at);
        displayedDate.setFullYear(displayedDate.getUTCFullYear());
        displayedDate.setMonth(displayedDate.getUTCMonth());
        displayedDate.setDate(displayedDate.getUTCDate());
        displayedDate.setHours(displayedDate.getUTCHours());
        displayedDate.setMinutes(displayedDate.getUTCMinutes());

        return (
            <div className="App">
                <form onSubmit={this.handleSubmit}>
                    <label>
                        Enter Team Name:
                        <input type="text" value={this.state.team_name} onChange={this.onTeamNameChanged} name="team_name"/>
                    </label>
                    <label>
                        Enter when this scrim will be played (EST)
                        <DatePicker
                            onChange={this.onPlayedAtChanged}
                            selected={displayedDate}
                            showTimeSelect={true}
                            utcOffset={0}
                            dateFormat="MMMM d, yyyy h:mm aa"
                            minDate={new Date()}
                        />
                    </label>
                    <label>
                        Enter Team Contact:
                        <input type="text" value={this.state.team_contact} onChange={this.onTeamContactChanged} name="team_contact"/>
                    </label>
                    <label>
                        Enter Maps
                        <input type="text" value={this.state.maps_text} onChange={this.onMapsChanged} name="maps"/>
                    </label>
                    <input type="submit" value="Submit" />
                </form>
            </div>
        );
    }
}

export default App;
