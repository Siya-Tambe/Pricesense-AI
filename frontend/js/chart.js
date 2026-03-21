let priceChart = null;

// ── Sale events calendar ────────────────────────────────────────

const SALE_EVENTS = [
  { name: "Big Billion Days",        month: 9,  day: 10 },
  { name: "Big Billion Days",        month: 9,  day: 11 },
  { name: "Great Indian Festival",   month: 9,  day: 15 },
  { name: "Great Indian Festival",   month: 9,  day: 16 },
  { name: "Diwali Sale",             month: 10, day: 1  },
  { name: "Flipkart Big Diwali",     month: 10, day: 5  },
  { name: "Amazon Freedom Sale",     month: 7,  day: 15 },
  { name: "Republic Day Sale",       month: 1,  day: 26 },
  { name: "Independence Day Sale",   month: 8,  day: 15 },
  { name: "End of Season Sale",      month: 6,  day: 20 },
  { name: "End of Season Sale",      month: 12, day: 20 },
  { name: "New Year Sale",           month: 12, day: 31 },
];

function getSaleEventsInRange(rawDates) {
  const events = [];
  rawDates.forEach((label, index) => {
    const date = new Date(label);
    if (isNaN(date)) return;
    const m = date.getMonth() + 1;
    const d = date.getDate();
    SALE_EVENTS.forEach(ev => {
      if (ev.month === m && Math.abs(ev.day - d) <= 1) {
        events.push({ index, name: ev.name });
      }
    });
  });
  return events;
}

function buildAnnotations(rawDates, actualData) {
  const annotations = {};
  const saleEvents = getSaleEventsInRange(rawDates);

  saleEvents.forEach((ev, i) => {
    annotations[`sale_${i}`] = {
      type: "line",
      xMin: ev.index,
      xMax: ev.index,
      borderColor: "rgba(245,158,11,0.4)",
      borderWidth: 1,
      borderDash: [4, 3],
      label: {
        display: true,
        content: "🏷️",
        position: "start",
        backgroundColor: "rgba(245,158,11,0.15)",
        color: "#f59e0b",
        font: { size: 11 },
        padding: { x: 5, y: 3 },
        borderRadius: 4,
      },
    };
  });

  return annotations;
}

// ── Build chart data ────────────────────────────────────────────

function buildChartData(priceHistory, forecastDay3, forecastDay7) {
  if (!priceHistory || priceHistory.length === 0) return null;

  const sorted = [...priceHistory].sort(
    (a, b) => new Date(a.date) - new Date(b.date)
  );

  const rawDates = sorted.map(h => h.date);

  const labels = sorted.map(h => {
    const d = new Date(h.date);
    return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
  });

  const actualPrices = sorted.map(h => h.price);

  const forecastLabels = [];
  const forecastRawDates = [];
  const forecastPrices = [];

  if (forecastDay3 || forecastDay7) {
    const lastDate = new Date(sorted[sorted.length - 1].date);

    if (forecastDay3) {
      const d3 = new Date(lastDate);
      d3.setDate(d3.getDate() + 3);
      forecastRawDates.push(d3.toISOString());
      forecastLabels.push(d3.toLocaleDateString("en-IN", { day: "numeric", month: "short" }));
      forecastPrices.push(forecastDay3);
    }

    if (forecastDay7) {
      const d7 = new Date(lastDate);
      d7.setDate(d7.getDate() + 7);
      forecastRawDates.push(d7.toISOString());
      forecastLabels.push(d7.toLocaleDateString("en-IN", { day: "numeric", month: "short" }));
      forecastPrices.push(forecastDay7);
    }
  }

  const allLabels    = [...labels, ...forecastLabels];
  const allRawDates  = [...rawDates, ...forecastRawDates];

  const actualData = [
    ...actualPrices,
    ...forecastLabels.map(() => null),
  ];

  const forecastData = [
    ...actualPrices.map(() => null),
    ...forecastPrices,
  ];

  if (forecastPrices.length > 0) {
    forecastData[actualPrices.length - 1] = actualPrices[actualPrices.length - 1];
  }

  return { allLabels, allRawDates, actualData, forecastData };
}

// ── Render chart ────────────────────────────────────────────────

function renderChart(canvasId, priceHistory, forecastDay3, forecastDay7) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const chartData = buildChartData(priceHistory, forecastDay3, forecastDay7);
  if (!chartData) {
    canvas.parentElement.innerHTML =
      '<p style="text-align:center;color:var(--text3);padding:40px 0;font-size:14px;">Not enough data to display chart</p>';
    return;
  }

  const { allLabels, allRawDates, actualData, forecastData } = chartData;

  if (priceChart) {
    priceChart.destroy();
    priceChart = null;
  }

  const ctx = canvas.getContext("2d");

  priceChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: allLabels,
      datasets: [
        {
          label: "Actual price",
          data: actualData,
          borderColor: "#6c63ff",
          backgroundColor: "rgba(108,99,255,0.07)",
          borderWidth: 2,
          pointRadius: 3,
          pointHoverRadius: 5,
          pointBackgroundColor: "#6c63ff",
          fill: true,
          tension: 0.3,
          spanGaps: false,
        },
        {
          label: "Forecast",
          data: forecastData,
          borderColor: "#a78bfa",
          backgroundColor: "transparent",
          borderWidth: 2,
          borderDash: [6, 4],
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: "#0a0a0f",
          pointBorderColor: "#a78bfa",
          pointBorderWidth: 2,
          fill: false,
          tension: 0.3,
          spanGaps: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: "index" },
      plugins: {
        legend: {
          display: true,
          position: "top",
          align: "end",
          labels: {
            font: { family: "DM Sans", size: 12 },
            color: "#9898b0",
            boxWidth: 24,
            padding: 16,
            usePointStyle: true,
          },
        },
        tooltip: {
          backgroundColor: "#1e1e28",
          titleColor: "#f0f0f8",
          bodyColor: "#9898b0",
          borderColor: "rgba(255,255,255,0.07)",
          borderWidth: 1,
          padding: 12,
          titleFont: { family: "DM Sans", size: 13, weight: "600" },
          bodyFont: { family: "DM Sans", size: 13 },
          callbacks: {
            label: (ctx) => {
              if (ctx.parsed.y === null) return null;
              return `  ${ctx.dataset.label}: ₹${Number(ctx.parsed.y).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
            },
            afterBody: (items) => {
              const idx = items[0]?.dataIndex;
              const saleEvents = getSaleEventsInRange(allRawDates);
              const match = saleEvents.find(e => e.index === idx);
              return match ? [`🏷️ ${match.name}`] : [];
            },
          },
        },
        annotation: {
          annotations: buildAnnotations(allRawDates, actualData),
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            font: { family: "DM Sans", size: 11 },
            color: "#55556a",
            maxTicksLimit: 8,
            maxRotation: 0,
          },
          border: { display: false },
        },
        y: {
          grid: { color: "rgba(255,255,255,0.04)" },
          ticks: {
            font: { family: "DM Sans", size: 11 },
            color: "#55556a",
            callback: (val) =>
              "₹" + Number(val).toLocaleString("en-IN", { maximumFractionDigits: 0 }),
          },
          border: { display: false },
        },
      },
    },
  });
}

// ── Annotate all-time low ───────────────────────────────────────

function annotateAllTimeLow(priceHistory) {
  if (!priceChart || !priceHistory || priceHistory.length === 0) return;
  const sorted = [...priceHistory].sort((a, b) => new Date(a.date) - new Date(b.date));
  const prices = sorted.map(h => h.price);
  const minPrice = Math.min(...prices);
  const minIndex = prices.indexOf(minPrice);

  if (!priceChart.options.plugins.annotation) {
    priceChart.options.plugins.annotation = { annotations: {} };
  }

  priceChart.options.plugins.annotation.annotations.allTimeLow = {
    type: "point",
    xValue: minIndex,
    yValue: minPrice,
    backgroundColor: "rgba(34,211,160,0.2)",
    borderColor: "#22d3a0",
    borderWidth: 2,
    radius: 6,
  };
  priceChart.update();
}