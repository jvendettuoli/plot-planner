'use strict';

//Cache common DOM elements
const $plantForm = $('#plant-form');
const $plantTableBody = $('#plant-table-body');
const $noResults = $('#no-results');

// Event handle on search form
$plantForm.submit(handleSearchSubmit);

/* 
Search Class handles requests and methods associated with updating the
plant table. This includes making axios requests to server, and 
extracting applicable data for the table display, and generating
HTML to show plants
*/
class Search {
	constructor() {}

	static defaultPlantImg = '/static/images/default-plant-pic.png';

	static async extractPlantData(item) {
		const imageUrl = item.image_url || this.defaultPlantImg;

		return {
			commonName       : item.common_name,
			slug             : item.slug,
			scientificName   : item.scientific_name,
			family           : item.family,
			familyCommonName : item.family_common_name,
			imageUrl         : imageUrl
		};
	}

	//GET request to plant_list view and calls for populating the data
	static async fetchAllPlants() {
		const res = await axios.get(`/plants`);
		let plantList = [];
		for (let item of res.data) {
			plantList.push(await this.extractPlantData(item));
		}
		await this.populateTable(plantList);
	}

	static async generatePlantRowHTML(plant) {
		return `
        <tr>
            <td>${plant.commonName}</td>
            <td><a href="/plants/${plant.slug}">${plant.scientificName}</a></td>
            <td>${plant.familyCommonName}</td>
			<td>
			<a type="button" data-toggle="modal" data-target="#${plant.slug}-modal">
            <img id="table-plant-img" class="img-thumbnail" src="${plant.imageUrl}" alt="${plant.commonName} image">
			</a>
			</td>
        </tr>`;
	}

	static async generatePlantImgModal(plant) {
		return `
		<div class="modal fade" id="${plant.slug}-modal" tabindex="-1" aria-labelledby="${plant.slug}-modal-label" aria-hidden="true">
			<div class="modal-dialog">
				<div class="modal-content">
					<img src="${plant.imageUrl}" alt="${plant.commonName} image">
				</div>
			</div>
		</div>`;
	}

	// Displays all plants returned by request, or No results found
	static async populateTable(plantList) {
		let plantTableData = '';
		for (let plant of plantList) {
			plantTableData = plantTableData.concat(await this.generatePlantRowHTML(plant));
			$('body').append(await this.generatePlantImgModal(plant));
		}

		if (plantTableData.length === 0) {
			$noResults.html('<h4 class="text-center my-3" style="width=100%">No results found.</h4>');
		}
		else {
			$noResults.empty();
		}
		$plantTableBody.html(plantTableData);
	}

	// POST request to return all plants based on search & filter terms
	// Also calls to display data and updates pagination links
	static async searchPlants(searchTerms) {
		const res = await axios.post(`/api/plants/search`, searchTerms);

		let plantList = [];
		for (let item of res.data[0]) {
			plantList.push(await this.extractPlantData(item));
		}
		const links = res.data[1];

		await this.populateTable(plantList);
		await Pagination.updateLinks(links);
	}
}

//On form submit, put form values into object and pass to
//searchPlants method.

function handleSearchSubmit(evt) {
	evt.preventDefault();
	let serializedInputs = $(this).serializeArray();
	let inputsObj = serializedInputs.reduce((obj, item) => {
		obj[item.name] = obj[item.name] ? [ ...obj[item.name], item.value ] : [ item.value ];

		return obj;
	}, {});

	Search.searchPlants(inputsObj);
}
