'use strict';

console.log('START plantSearch.js');

//Cache common DOM elements
const $plantForm = $('#plant-form');
const $plantTableBody = $('#plant-table-body');
const $noResults = $('#no-results');

class Search {
	constructor() {
		//Change out based on deployment
		this.baseURL = 'http://127.0.0.1:5000';
	}
	//Change out based on deployment
	static baseUrl = 'http://127.0.0.1:5000';
	static defaultImg = '/static/images/default-pic.png';

	static async extractPlantData(item) {
		const imageUrl = item.image_url || this.defaultImg;

		return {
			commonName       : item.common_name,
			slug             : item.slug,
			scientificName   : item.scientific_name,
			family           : item.family,
			familyCommonName : item.family_common_name,
			imageUrl         : imageUrl
		};
	}

	//GET request to plant_list view
	static async fetchAllPlants() {
		console.log('FETCHING ALL PLANTS');
		const res = await axios.get(`${this.baseUrl}/plants`);

		let plantList = [];
		for (let item of res.data) {
			plantList.push(await this.extractPlantData(item));
		}
		console.log('plantList', plantList);

		await this.populateTable(plantList);
	}

	static async generatePlantRowHTML(plant) {
		return `
        <tr>
            <td>${plant.commonName}</td>
            <td><a href="/plants/${plant.slug}">${plant.scientificName}</a></td>
            <td>${plant.familyCommonName}</td>
            <td><img width="100" height="100" src="${plant.imageUrl}" alt="${plant.commonName} image"></td>
        </tr>`;
	}

	static async populateTable(plantList) {
		console.log('IN Populate');
		let plantTableData = '';
		for (let plant of plantList) {
			// console.log(plant);
			// console.log(await this.generatePlantRowHTML(plant));
			plantTableData = plantTableData.concat(await this.generatePlantRowHTML(plant));
		}

		if (plantTableData.length === 0) {
			$noResults.html('<h4 class="text-center my-3" style="width=100%">No results found.</h4>');
		}
		else {
			$noResults.empty();
		}
		$plantTableBody.html(plantTableData);
	}

	static async searchPlants(searchTerms) {
		console.log('SEARCHING PLANTS');
		console.log('searchTerms', searchTerms);

		const res = await axios.post(`${this.baseUrl}/api/plants/search`, searchTerms);
		console.log('RES', res);
		console.log('RES.data', res.data);

		let plantList = [];
		for (let item of res.data[0]) {
			plantList.push(await this.extractPlantData(item));
		}
		// console.log('plantList', plantList);
		const links = res.data[1];

		await this.populateTable(plantList);
		await Pagination.updateLinks(links);
	}
}

//On form submit, put form values into object and pass to
//searchPlants method.
$plantForm.submit(function(evt) {
	evt.preventDefault();

	let serializedInputs = $(this).serializeArray();
	console.log('Serialized', serializedInputs);

	let inputsObj = serializedInputs.reduce((obj, item) => {
		obj[item.name] = obj[item.name] ? [ ...obj[item.name], item.value ] : [ item.value ];
		// if (item.name in Object.keys(obj)) {
		// 	console.log(item.name);
		// 	if (Array.isArray(obj[item.name])) {
		// 		console.log('in array');
		// 		obj[item.name] = obj[item.name].push(item.value);
		// 	}
		// 	else {
		// 		console.log('first go');
		// 		obj[item.name] = [ obj[item.name], item.value ];
		// 	}
		// }
		// else {
		// 	console.log('skippy', item.name, item.value, obj);
		// 	obj[item.name] = item.value;
		// }

		return obj;
	}, {});
	console.log('InputObj', inputsObj);

	Search.searchPlants(inputsObj);
});
