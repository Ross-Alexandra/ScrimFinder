import React, {Component} from 'react';
import CancelOutlinedIcon from '@material-ui/icons/CancelOutlined';


class MapIcon extends Component {

    constructor(props) {
        super(props);

        this.state = {
            picker: false,
            hovering: false
        }
    }

    toggle_picker = () => {
        const picker = !this.state.picker;
        this.setState({picker});
    }

    select_map = (selected) => {
        this.props.add_map(selected);
        this.toggle_picker();
    }

    set_hovering = () => {
        this.setState({hovering: true});
    }

    unset_hovering = () => { 
        this.setState({hovering: false});
    }

    render() {
        const map_tiles = ["no preference", "villa", "consulate", "kafe", "cancel", "coastline", "clubhouse", "oregon", "chalet"]
                            .map((val, indx, arr) => {
                                const onClick = val === "cancel" ? () => {} : () => this.select_map(val);

                                return (
                                    <div
                                        key={indx}
                                        className="Scrim-information-map-selector-picker-tile"
                                        onClick={onClick}
                                        style={{background: 'url(/' + val.replace(" ", "_") + ".png)"}}
                                    >
                                    </div>
                                );
                            });

        const isAddMap = this.props.map_name === "add map";

        const onClick = isAddMap ? this.toggle_picker : () => {};
        const setHovering = isAddMap ? () => {} : this.set_hovering;
        const unsetHovering = isAddMap ? () => {} : this.unset_hovering;
        const bgImage = '/' + this.props.map_name.replace(" ", "_") + ".png";

        return (
            <div
                className="Scrim-information-map-selector-border"
                style={this.props.error ? {backgroundImage: "linear-gradient(to right, #f44336, #f44336)"} : {}}
                onMouseEnter={() => {setHovering(); onClick();}}
                onMouseLeave={() => {unsetHovering(); onClick();}}>
                {
                    this.state.picker === false ? (
                        <div 
                            className="Scrim-information-map-selector-body"
                            style= {{background: "url("+bgImage+")"}}
                        >
                            { this.props.map_name !== "add map" && this.state.hovering ? 
                                <div
                                    className="Scrim-information-map-selector-picker-remove"
                                    onClick={() => {this.props.remove_map(this.props.position)}}    
                                >
                                    <CancelOutlinedIcon/>
                                </div>
                            :
                                null
                            }  
                            <text style={this.props.error ? {color: "#f44336"} : {}}></text>
                        </div>
                    ) : (
                        <div className="Scrim-information-map-selector-picker">
                            {map_tiles}
                        </div>
                    )
                }
            </div>
        );
    }
}

export default MapIcon;