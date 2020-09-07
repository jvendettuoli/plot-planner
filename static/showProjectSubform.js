'use strict';

//Set common strings to variable
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
$('ul').on('click', '.proj-rmv-plot-btn', handleRemovePlotConn);
// On click of X btn on connected plantlists
$('ul').on('click', '.proj-rmv-plntlst-btn', handleRemovePlantlistConn);

// Toggles displaying plot add form
$togglePlotsBtn.click(function(evt) {
	$plotsForm.toggle('fast');
});
// Toggles displaying plantlist add form
$togglePlantlistsBtn.click(function(evt) {
	$plantlistsForm.toggle('fast');
});

// Handles Projects - Plots connections between subforms and connected lists
$plotsForm.submit(handleAddPlotSubmit);

// Handles Projects - Plant List connections between subforms and connected lists
$plantlistsForm.submit(handleAddPlantlistSubmit);

function generateOptionHTML(value, text) {
	return `
	<option value="${value}">${text}</option>
	`;
}

// Removes the project-plot connection, and updates connected
// projects list and project add form
function handleRemovePlotConn(evt) {
	const $li = $(evt.currentTarget).parent();
	const plotId = $(evt.currentTarget).parent().attr(dataAttrPlotId);
	const projectId = $li.attr(dataAttrProjectId);

	Connection.projectRemovePlot(projectId, plotId);
	$li.remove();

	$('#plots').append(generateOptionHTML(plotId, $li.text()));
}

// Removes the project-plantlist connection, and updates connected
// plantlists list and plantlist add form
function handleRemovePlantlistConn(evt) {
	evt.preventDefault();
	const $li = $(evt.currentTarget).parent();
	const projectId = $li.attr(dataAttrProjectId);
	const plantlistId = $li.attr(dataAttrPlantListId);

	Connection.projectRemovePlantList(projectId, plantlistId);
	$li.remove();

	$('#plantlists').append(generateOptionHTML(plantlistId, $li.text()));
}

// Generates HTML for connected lists based on connection type
function generateLiHtml(element, projectId, elementId, elementName) {
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
	<li data-${element}-id=${elementId} data-project-id=${projectId}><a href="/${element}s/${elementId}">${elementName} </a><button class="btn btn-sm text-danger ${rmvClass}"> <i class="fas fa-times"></i></button></li>
	`;

	return li;
}

// On add plot form submit updates plot form and connected plot
// list. Makes connection for all selected values
function handleAddPlotSubmit(evt) {
	evt.preventDefault();

	const projectId = $(evt.currentTarget).closest('[data-project-id]').attr(dataAttrProjectId);
	let serializedInputs = $(this).serializeArray();

	// For each input, connect the project and plots, and update the Connected plots list and plots form to reflect the new connection.
	serializedInputs.forEach((element) => {
		if (element.name !== 'csrf_token') {
			Connection.projectAddPlot(projectId, element.value);
			const optionText = $(`option:selected[value='${element.value}']`).text();
			if ($projectList.text().includes('No plots connected yet.')) {
				$projectList.empty();
			}
			$projectList.append(generateLiHtml('plot', projectId, element.value, optionText));
			$(`option:selected[value='${element.value}']`).remove();
		}
	});
}

// On add plantlist form submit updates plantlist form and connected
// plantlist list. Makes connection for all selected values
function handleAddPlantlistSubmit(evt) {
	evt.preventDefault();

	const projectId = $(evt.currentTarget).closest('[data-project-id]').attr(dataAttrProjectId);

	let serializedInputs = $(this).serializeArray();

	// For each input, connect the plot and plantlist, and update the Connected Plots list and Plots form to reflect the new connection.
	serializedInputs.forEach((element) => {
		if (element.name !== 'csrf_token') {
			Connection.projectAddPlantList(projectId, element.value);
			const optionText = $(`option:selected[value='${element.value}']`).text();
			if ($plantlistList.text().includes('No plant lists connected yet.')) {
				$plantlistList.empty();
			}
			$plantlistList.append(generateLiHtml('plantlist', projectId, element.value, optionText));
			$(`option:selected[value='${element.value}']`).remove();
		}
	});
}
