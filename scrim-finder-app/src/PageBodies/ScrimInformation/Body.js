import 'date-fns';
import React, {Component} from 'react';
import {MenuItem, TextField} from '@material-ui/core';
import { createMuiTheme } from '@material-ui/core/styles';
import {ThemeProvider} from '@material-ui/styles';
import DateFnsUtils from '@date-io/date-fns';
import {
  MuiPickersUtilsProvider,
  DateTimePicker
} from '@material-ui/pickers';

import './ScrimInformation.css';

class Body extends Component {

    render() {

        const minDate = new Date();
        minDate.setHours(minDate.getHours() - 1);

        const theme = createMuiTheme({
            overrides: {
                MuiFormControl: {
                    root: {
                        width: "80%"
                    }
                },
                MuiFormLabel: {
                    root: {
                        color: "#ffffff",
                    }
                },
                MuiFilledInput: {
                    root: {
                        backgroundColor: "#333437"
                    },
                },
                MuiInputBase: {
                    input: {
                        color: "#ffffff",
                    }
                },
                MuiFormHelperText: {
                    root: {
                        color: "#ffffff",
                    }
                }
            }
        });

        const team_name_error = !!this.props.errors["Team Name"]
        const scrim_type_error = !!this.props.errors["Scrim Type"]
        const played_at_error = !!this.props.errors["Played At"]
        const team_contact_error = !!this.props.errors["Team Contact"]

        const team_name_text = team_name_error ? this.props.errors["Team Name"] : "The name of the team which is looking for a scrim"
        const scrim_type_text = scrim_type_error ? this.props.errors["Scrim Type"] : "The type of scrim your team is looking for."
        const played_at_text = played_at_error ? this.props.errors["Played At"] : "The date and time you would like to play."
        const team_contact_text = team_contact_error ? this.props.errors["Team Contact"] : "The Discord Tag of the team's contact."

        return(
            <div className="Scrim-information-body">
                <ThemeProvider theme={theme}>
                    <div className="Scrim-information-body-selector Scrim-information-team-name-selector">
                        <TextField
                            variant="filled"
                            onChange={this.props.onTeamNameChanged}
                            label="Team Name"
                            error={team_name_error}
                            helperText={team_name_text}
                        />
                    </div>
                    <div className="Scrim-information-body-selector Scrim-information-scrim-type-selector">
                        <TextField
                                variant="filled"
                                onChange={this.props.onScrimTypeChanged}
                                label="Scrim Type"
                                error={scrim_type_error}
                                helperText={scrim_type_text}
                                select={true}
                            >
                            <MenuItem value="gameday">Gameday</MenuItem>
                            <MenuItem value="6-6">6-6</MenuItem>
                            <MenuItem value="no preference">No preference</MenuItem>
                        </TextField>
                    </div>
                    <div className="Scrim-information-body-selector Scrim-information-played-at-selector">
                        <MuiPickersUtilsProvider utils={DateFnsUtils}>
                        <DateTimePicker
                            inputVariant="filled"
                            label="Played At"
                            format="MMMM d, yyyy h:mm aa"
                            error={played_at_error}
                            helperText={played_at_text}
                            minDate={minDate}
                            minutesStep={30}
                            minDateMessage={"This is a test."}
                            value={this.props.displayedDate}
                            onChange={this.props.onPlayedAtChanged}
                        />
                        </MuiPickersUtilsProvider>
                    </div>
                    <div className="Scrim-information-body-selector Scrim-information-team-contact-selector">
                        <TextField
                                variant="filled"
                                onChange={this.props.onTeamContactChanged}
                                label="Team Contact"
                                error={team_contact_error}
                                helperText={team_contact_text}
                            />
                    </div>
                </ThemeProvider>
            </div>
        );
    }
}

export default Body;