// const palette = ['rgba(171, 235, 210, 0.8)', 'rgba(57, 208, 150, 0.8)']
const palette = ['rgba(255, 0, 0, 0.8)', 'rgba(150, 0, 0, 0.8)']

const palettebg = palette.map(x => x.replace('0.8', '0.6'))
const misccolor = 'rgba(255, 255, 255, 0.9)'

const chartoptions = {
	scales: {
		x: { ticks: {color: misccolor}},
		y: { ticks: {color: misccolor}}
	},
	animation: true,
	plugins: {
		legend: {display: true, labels: {color: misccolor}},
		tooltip: {enabled: true},	
	},
}

async function plottoday(data, historic) {

	let time = data['time']
	let nres = data['nres']
	
	// get historic data for today's day of week
	let date = new Date()
	let d = date.getDay()
	let today = historic[d]

	// get only times that concern us
	let firsttime = time[0]
	let starttimeidx = today['times'].indexOf(firsttime)
	let historicnres = today['mres'].slice(starttimeidx)

	new Chart(document.getElementById('chart'), {
		type: 'line',
		options: chartoptions,
		data: {
			labels : time,
			datasets: [
			{
				label: 'Current',
				data: nres,
				fill: true,
				borderColor: palette[0],
				backgroundColor: palettebg[0],
				tension: 0.4,
			},
			{
				label: 'Historic average',
				data: historicnres,
				fill: true,
				borderColor: palette[1],
				backgroundColor: palettebg[1],
				tension: 0.4,
			},
			],
		},
		})
		
};

async function loadjson(filename){
	return fetch(filename)
		.then(response => response.json())
		.then(responseJson => { return responseJson;})
		.catch(error => {
			console.error('Error:', error);
		});
}

async function adjustheader(data){
		// current reservations
		let uts = data['updatetime']
		let put = Date.parse(uts)
		let hourofupdate = new Date(put).getHours()
		let date = new Date()
		let nowstr = 'Today, '
		if (hourofupdate > 21) {
			nowstr = 'Tomorrow, '
			date.setDate(date.getDate()+1)
		}
		nowstr = nowstr + date.toDateString()
		let putd = new Date(put)
		nowstr = nowstr + "<br>Updated at " + putd.getHours()+':'+putd.getMinutes()
	
		document.getElementById('now').innerHTML = nowstr
		return date.getDay()-1 // to be used with my dict that is 0=monday
}

async function plothistoric(historic, daytoshow=-1, histchart) {

	
	let date = new Date()
	var d;
	if (daytoshow < 0 || daytoshow > 6){
		d = date.getDay() - 1
		d < 0 ? d = 6 : d
	} else {
		d = daytoshow
	}

	let data = historic[d]
	let time = data['times']
	let nres = data['mres']
	
	nolegend = {...chartoptions}
	nolegend['plugins']['legend']['display'] = false

	if (typeof histchart !== 'undefined') {
		histchart.data = {
			labels : time,
			datasets: [
			{
				label: 'Reservations',
				data: nres,
				fill: true,
				borderColor: palette[1],
				backgroundColor: palettebg[1],
				tension: 0.4,
			},
			],
		}
		histchart.update()
	}else{
		histchart = new Chart(document.getElementById('histchar'), {
			type: 'line',
			options: nolegend,
			data: {
				labels : time,
				datasets: [
				{
					label: 'Reservations',
					data: nres,
					fill: true,
					borderColor: palette[1],
					backgroundColor: palettebg[1],
					tension: 0.4,
				},
				],
			},
			})
		}

		let week = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday", "Sunday"];
		let day = week[d]
		el = document.getElementById('dyntitle')
		el.innerHTML = 'Historic reservation data for ' + day
		return [historic, d, histchart]
	};

async function caller(){
	const historic = await loadjson('histdict.json');
	const today = await loadjson('today.json');
	plottoday(today, historic);
	plottedday = await adjustheader(today);
	const histbundle = await plothistoric(historic, plottedday);
	return histbundle
}

var histbundle = caller()

const buttons = document.getElementsByClassName("arrow");
const buttonPressed = e => {
	let id = e.target.id
	// console.log(id === 'nextday')
	if (id==='nextday'){
		histbundle.then( ([historic, d, chart]) => {
			d = (d+1) % 7
			histbundle = plothistoric(historic, d, chart)
		})
	} else if (id==='prevday'){
		histbundle.then( ([historic, d, chart]) => {
			d = d - 1
			d<0 ? d = 6 : d
			histbundle = plothistoric(historic, d, chart)
		})
	}
}

for (let button of buttons){
	button.addEventListener('click', buttonPressed);
}