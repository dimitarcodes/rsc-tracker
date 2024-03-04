
async function plot(data, historic) {
    console.log(data);
    console.log(historic);

    const time = data['time']
    const nres = data['nres']
    
    const updatetime = data['updatetime']

    var firsttime = time[0]
    var date = new Date()
    var d = date.getDay()

    console.log(d)
    var today = historic[d]
    console.log(today)
    var starttimeidx = today['times'].indexOf(firsttime)
    console.log(starttimeidx)

    var historictime = today['times'].slice(starttimeidx)
    var historicnres = today['mres'].slice(starttimeidx)


    const trace = {
        x: time,
        y: nres,
        mode: 'lines+marekrs',
        type: 'scatter',
        name: 'Current<br>Reservations'
    };

    const historictrace = {
        x: historictime,
        y: historicnres,
        mode: 'lines+marekrs',
        type: 'scatter',
        name: 'Historic<br>Reservations'
    };

    const layout = {
        autosize: false,
        width: 500,
        paper_bgcolor: '#f5f5f5',
        automargin: true,
        title: 'Number of reservations at the RSC Gym<br>Last Updated: ' + updatetime,
        xaxis: {
            title: 'Timeslot',
            fixedrange: true,
        },
        yaxis: {
            title: 'Value',
            fixedrange: true,
            range: [0,60]
        }
        
    };
    
    Plotly.newPlot('plotlydiv', [trace, historictrace], layout);
}

async function loadjson(filename){
    return fetch(filename)
        .then(response => response.json())
        .then(responseJson => { return responseJson;})
        .catch(error => {
            console.error('Error:', error);
        });
}

async function caller(){
    const historic = await loadjson('histdict.json');
    const today = await loadjson('today.json');
    plot(today, historic);
}

caller()