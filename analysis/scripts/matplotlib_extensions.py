import matplotlib.pyplot as plt
import numpy as np

def setup_timeseries_plot(ax=None,width=10,height=6,label_fontsize=14,axis_fontsize=12):
    if ax is None:
        fig = plt.figure(figsize=(width,height))
        ax = plt.gca()
    ax.tick_params(axis="both", labelsize=axis_fontsize)
    ax.xaxis.label.set_size(label_fontsize)
    ax.yaxis.label.set_size(label_fontsize)
    ax.xaxis.label.set_fontweight('light')
    ax.yaxis.label.set_fontweight('light')
    for label in ax.get_xticklabels():
        label.set_fontweight("light")  
    for label in ax.get_yticklabels():
        label.set_fontweight("light") 
    ax.grid(which="both", lw=0.5, ls=":")
    return ax

def labelled_pie(data,labels,title,ax=None,**kwargs):
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4), subplot_kw=dict(aspect="equal"))

    settings = dict(wedgeprops=dict(width=0.5,edgecolor="white"),
        startangle=0,
        autopct="%1.1f%%",
        pctdistance=0.75,
        labeldistance=0.75)
    
    settings.update(**kwargs)
    # Draw the actual pie/donut
    wedges, texts, percentages = ax.pie(
        data,
        **settings
    )
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.0)
    kw = dict(
        arrowprops=dict(arrowstyle="-", color="gray", lw=0.5),
        bbox=bbox_props,
        zorder=0,
        va="center",
    )
    # Set properites of the percentage labels
    for autotext in percentages:
        autotext.set_color("white")
        autotext.set_fontsize(14)
        autotext.set_fontweight("normal")
        autotext.set_zorder(1)

    # Now label the sections for every country
    # See https://matplotlib.org/stable/gallery/pie_and_polar_charts/pie_and_donut_labels.html
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(
           labels[i],
            xy=(x, y),
            xytext=(1.25 * np.sign(x), 1.3 * y),
            horizontalalignment=horizontalalignment,
            fontsize=20,
            fontweight="light",
            color="black",
            **kw,
        )


    plt.title(title, fontsize=30, fontweight="light")
    return ax