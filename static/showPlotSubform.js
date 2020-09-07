'use strict';

//Set common strings to variables
const dataAttrProjectId = 'data-project-id';
const dataAttrPlotId = 'data-plot-id';
const dataAttrPlantListId = 'data-plantlist-id';

//Cache common DOM elements
const $projRmvPlotBtn = $('.proj-rmv-plot-btn');
const $projRmvPlntlstBtn = $('.proj-rmv-plntlst-btn');
const $plotRmvPlntLstBtn = $('.plot-rmv-plntlst-btn');
const $toggleProjectsBtn = $('#toggle-projects-btn');
const $togglePlotsBtn = $('#toggle-plots-btn');
const $togglePlantlistsBtn = $('#toggle-plantlists-btn');
const $projectsForm = $('#add-projects-form');
const $plotsForm = $('#add-plots-form');
const $plantlistsForm = $('#add-plantlists-form');
const $plotList = $('#plot-list');
const $projectList = $('#project-list');
const $plantlistList = $('#plantlist-list');
const $modalBody = $('.modal-body');

// On click of X btn on connected project
$('ul').on('click', '.proj-rmv-plot-btn', handleRemoveProjectConn);
// On click of X btn on connected plantlists
$('ul').on('click', '.plot-rmv-plntlst-btn', handleRemovePlantlistConn);

// Toggles displaying project add form
$toggleProjectsBtn.click(function(evt) {
	$projectsForm.toggle('fast');
});
// Toggles displaying plantlist add form
$togglePlantlistsBtn.click(function(evt) {
	$plantlistsForm.toggle('fast');
});

// Handles Projects - Plots connections between subforms and connected lists
$projectsForm.submit(handleAddProjectSubmit);

// Handles Plots - Plant List connections between subforms and connected lists
$plantlistsForm.submit(handleAddPlantlistSubmit);

function generateOptionHTML(value, text) {
	return `
	<option value="${value}">${text}</option>
	`;
}

// Removes the project-plot connection, and updates connected
// projects list and project add form
function handleRemoveProjectConn(evt) {
	const $li = $(evt.currentTarget).parent();
	const plotId = $(evt.currentTarget).parent().attr(dataAttrPlotId);
	const projectId = $li.attr(dataAttrProjectId);

	Connection.projectRemovePlot(projectId, plotId);
	$li.remove();

	$('#projects').append(generateOptionHTML(projectId, $li.text()));
}

// Removes the plot-plantlist connection, and updates connected
// plantlists list and plantlist add form
function handleRemovePlantlistConn(evt) {
	evt.preventDefault();
	const $li = $(evt.currentTarget).parent();
	const plotId = $li.attr(dataAttrPlotId);
	const plantlistId = $li.attr(dataAttrPlantListId);

	Connection.plotRemovePlantList(plotId, plantlistId);
	$li.remove();

	$('#plantlists').append(generateOptionHTML(plantlistId, $li.text()));

	//Remove the option from the Plot Design plantlist select
	$plantlistSelect.children(`[value="${plantlistId}"]`).remove();
}

// Generates HTML for connected lists based on connection type
function generateLiHtml(element, plotId, elementId, elementName) {
	let rmvClass;
	if (element === 'project') {
		rmvClass = 'proj-rmv-plot-btn';
	}
	else if (element === 'plot') {
		rmvClass = 'plot-rmv-plntlst-btn';
	}
	else if (element === 'plantlist') {
		rmvClass = 'plot-rmv-plntlst-btn';
	}
	const li = `
	<li data-${element}-id=${elementId} data-plot-id=${plotId}><a href="/${element}s/${elementId}">${elementName} </a><button class="btn btn-sm text-danger ${rmvClass}"> <i class="fas fa-times"></i></button></li>
	`;

	return li;
}

// On add project form submit updates project form and connected project
// list. Makes connection for all selected values
function handleAddProjectSubmit(evt) {
	evt.preventDefault();

	const plotId = $(evt.currentTarget).closest('[data-plot-id]').attr(dataAttrPlotId);
	let serializedInputs = $(this).serializeArray();

	// For each input, connect the project and plot, and update the Connected Projects list and Projects form to reflect the new connection.
	serializedInputs.forEach((element) => {
		if (element.name !== 'csrf_token') {
			Connection.projectAddPlot(element.value, plotId);
			const optionText = $(`option:selected[value='${element.value}']`).text();
			if ($projectList.text().includes('No projects connected yet.')) {
				$projectList.empty();
			}
			$projectList.append(generateLiHtml('project', plotId, element.value, optionText));
			$(`option:selected[value='${element.value}']`).remove();
		}
	});
}

// On add plantlist form submit updates plantlist form and connected
// plantlist list. Makes connection for all selected values
function handleAddPlantlistSubmit(evt) {
	evt.preventDefault();

	const plotId = $(evt.currentTarget).closest('[data-plot-id]').attr(dataAttrPlotId);
	let serializedInputs = $(this).serializeArray();

	// For each input, connect the plot and plantlist, and update the Connected Plots list and Plots form to reflect the new connection.
	serializedInputs.forEach((element) => {
		if (element.name !== 'csrf_token') {
			Connection.plotAddPlantList(plotId, element.value);
			const optionText = $(`option:selected[value='${element.value}']`).text();
			if ($plantlistList.text().includes('No plant lists connected yet.')) {
				$plantlistList.empty();
			}
			$plantlistList.append(generateLiHtml('plantlist', plotId, element.value, optionText));
			$(`option:selected[value='${element.value}']`).remove();

			//remove from Plot Design Plantlist Select list
			$plantlistSelect.append(generateOptionHTML(element.value, optionText));
		}
	});
}
