from presenters.common.tab_change_handlers import TAB_LOADERS

def on_tab_changed(parent, index):
    tab_name = parent.tab_widget.tabText(index)
    loader = TAB_LOADERS.get(tab_name)

    if loader and parent.org_name:
        loader(parent)