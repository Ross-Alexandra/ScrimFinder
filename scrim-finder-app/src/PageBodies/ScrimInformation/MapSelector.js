import React, {Component} from 'react';
import MapIcon from './MapIcon';

import ArrowLeftIcon from '@material-ui/icons/ArrowLeft';
import ArrowRightIcon from '@material-ui/icons/ArrowRight';

import './ScrimInformation.css';

class MapSelector extends Component {

    constructor(props) {
        super(props);

        this.maps = {
            Kafe: "kafe",
            Villa: "villa",
            Oregon: "oregon",
            Coastline: "coastline",
            Chalet: "chalet",
            Consulate: "consulate",
            Clubhouse: "clubhouse",
            NoPreference: "no preference"
        }

        this.state = {
            maps: [],
            position: 0,
            arrows_visible: false
        }
    }

    add_map = (map) => {
        const maps = this.state.maps;
        maps.push(map);
        this.setState({maps});

        this.props.onMapsChanged(maps);
        if (maps.length >= 3) {
            this.incr_position();
        }
    }

    remove_map = (map_index) => {
        const maps = this.state.maps;
        maps.splice(map_index, 1);

        this.setState({maps});
        this.props.onMapsChanged(maps);

        // -1 because there were maps.length + 1 total cards 
        // before we removed one; now that we've removed one it's like doing
        // + 1 + 1 - 3 = -1.
        // Thus, if we're equal to this number, then we were 
        // previously on the right border, so we need to decrement
        // in order to stay on the right border.
        if (this.state.position === maps.length - 1) {
            this.decr_position();
        }
    }

    incr_position = () => {
        // -2 because there are maps.length + 1 total cards,
        // so rather than doing length + 1 - 3 just do -2.
        if (this.state.position < this.state.maps.length - 2) {
            this.setState({position: this.state.position + 1});
        }
    }

    decr_position = () => {
        if (this.state.position > 0) {
            this.setState({position: this.state.position - 1});
        }
    }

    show_arrows = () => {
        this.setState({arrows_visible: true});
    }

    hide_arrows = () => {
        this.setState({arrows_visible: false});
    }

    render() {

        var map_icons = this.state.maps.map((value, index, arr) => {            
            return <MapIcon            
                map_name={value}
                position={index} // Silly workaround since key gets eaten.
                key={index}
                remove_map={this.remove_map}
                error={!!this.props.error}
            />
        });
        map_icons.push(
            <MapIcon
                map_name={"add map"}
                key={map_icons.length}
                add_map={this.add_map}
                error={!!this.props.error}
            />
        );

        const too_many_icons = map_icons.length > 3;
        const left_barrier = this.state.position === 0;
        const right_barrier = this.state.position === map_icons.length - 3;

        if (too_many_icons) {
            map_icons = map_icons.slice(this.state.position, this.state.position + 3);
        }

        const left_arrow = (
            <div className="Scrim-information-arrow-box" onClick={this.decr_position}><ArrowLeftIcon/></div>
        );
        const right_arrow = (
            <div className="Scrim-information-arrow-box" onClick={this.incr_position}><ArrowRightIcon/></div>
        );

        return(
            <React.Fragment>
                <div
                    className="Scrim-information-map-selector"
                    onMouseEnter={this.show_arrows}
                    onMouseLeave={this.hide_arrows}
                >
                    {too_many_icons && this.state.arrows_visible && !left_barrier ? 
                        left_arrow 
                    : 
                        <div className="Scrim-information-arrow-placeholder"/>
                    }
                    {map_icons}
                    {too_many_icons && this.state.arrows_visible && !right_barrier ? 
                        right_arrow
                    :
                        <div className="Scrim-information-arrow-placeholder"/>
                    }
                    { this.props.error ?
                        <React.Fragment>
                            <div className="break"></div>
                            <div className="Scrim-information-map-selector-error-box">
                                <text className="Scrim-information-map-selector-error">
                                    {this.props.error}
                                </text>
                            </div>
                        </React.Fragment>
                    :
                        null
                    }
                </div>
            </React.Fragment>
        );
    }
}

export default MapSelector;