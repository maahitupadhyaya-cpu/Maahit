import Plotly from "plotly.js-dist-min";
import createPlotlyComponent from "react-plotly.js/factory";

const Plot = createPlotlyComponent(Plotly as any);

export { Plotly };
export default Plot;
