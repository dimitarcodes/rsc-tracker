
function plot(data) {
    console.log(data);
    const time = data['time']
    const nres = data['nres']
    
    const updatetime = data['updatetime'
]
    const trace = {
        x: time,
        y: nres,
        mode: 'lines+marekrs',
        type: 'scatter'
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
    
    Plotly.newPlot('plotlydiv', [trace], layout);
}

fetch('today.json')
    .then(response => response.json())
    .then(data => {
        plot(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });


