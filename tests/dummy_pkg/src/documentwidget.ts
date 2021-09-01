// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import { DocumentWidget } from "@jupyterlab/docregistry";
import { SpreadsheetWidget } from "./widget";
import { ToolbarButton } from "@jupyterlab/apputils";
import { LabIcon } from "@jupyterlab/ui-components";
import addRowSvg from "../style/icons/mdi-table-row-plus-after.svg";
import removeRowSvg from "../style/icons/mdi-table-row-remove.svg";
import { nullTranslator, TranslationBundle } from "@jupyterlab/translation";

export class SpreadsheetEditorDocumentWidget extends DocumentWidget<SpreadsheetWidget> {
  protected _trans: TranslationBundle;

  constructor(options: DocumentWidget.IOptions<SpreadsheetWidget>) {
    super(options);
    const translator = options.translator || nullTranslator;
    this._trans = translator.load("spreadsheet-editor");

    const addRowButton = new ToolbarButton({
      icon: new LabIcon({ name: "spreadsheet:add-row", svgstr: addRowSvg }),
      onClick: () => {
        this.content.jexcel.insertRow();
        this.content.updateModel();
      },
      tooltip: this._trans.__("Insert a row at the end"),
    });
    this.toolbar.addItem("spreadsheet:insert-row", addRowButton);

    const removeRowButton = new ToolbarButton({
      icon: new LabIcon({
        name: "spreadsheet:remove-row",
        svgstr: removeRowSvg,
      }),
      onClick: () => {
        this.content.jexcel.deleteRow(this.content.jexcel.rows.length - 1, 1);
        this.content.updateModel();
      },
      tooltip: this._trans.__("Remove the last row"),
    });
    this.toolbar.addItem("spreadsheet:remove-row", removeRowButton);
  }
}
