'use strict';

//Handles requests to server database query endpoints
class Query {
	constructor() {
		//Change out based on deployment
		this.baseURL = 'https://plot-planner.herokuapp.com';
	}
	//Change out based on deployment
	static baseUrl = 'https://plot-planner.herokuapp.com';

	//GET request to get connections based on a primaryId and secondary type
	static async getConnections(primaryType, primaryId, secondaryType) {
		const res = await axios.get(`${this.baseUrl}/query/${primaryType}/${primaryId}/${secondaryType}`);
		return res.data;
	}

	//GET request to get data associated with single plantlist (plantlist_plants_id, plant common name, plant id, and plant symbol ). Currently used for populating plantlist data on Plot Design
	static async getPlantlistData(plantlistId) {
		const res = await axios.get(`${this.baseUrl}/query/plantlist/${plantlistId}`);
		return res.data;
	}
	//GET request to getting symbols assoicated with each plot cell.
	static async getPlotCellSymbols(plotId) {
		const res = await axios.get(`${this.baseUrl}/query/plot_cells/${plotId}`);
		return res.data;
	}
}
