import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ActivatedRoute } from '@angular/router';
import { ConfigEditor } from '@app-interfaces/configEditor';
import { SourceDb } from '@app-interfaces/sourceDb';
import { ConfigEditorService } from '@app-services/config-editor/config-editor.service';
import { SourceDbService } from '@app-services/source-db/source-db.service';

@Component({
  selector: 'app-dms-config-editor',
  templateUrl: './dms-config-editor.component.html',
  styleUrls: ['./dms-config-editor.component.scss']
})
export class DmsConfigEditorComponent implements OnInit {

  dbId?: string
  sourceDb?: SourceDb
  config?: ConfigEditor = {
    is_configured: true,
    dms_config_values: {
      port: 5432,
      username: "postgres",
      password: "waverunner-test"
    }
  }
  configForm: FormGroup

  constructor(
    private configEditorService: ConfigEditorService,
    private sourceDbService: SourceDbService,
    private activatedRoute: ActivatedRoute,
    private formBuilder: FormBuilder,
    private snackBar: MatSnackBar,
  ) {
    this.configForm = this.formBuilder.group({
      is_configured: new FormControl(false, []),
      dms_config_values: new FormGroup({
        port: new FormControl(5432, []),
        username: new FormControl('', []),
        password: new FormControl('', []),
      })
    })
  }

  ngOnInit(): void {
    this.activatedRoute.queryParams.subscribe((params) => {
      this.dbId=params.databaseId;
      this.loadDb()
    })
  }

  loadDb() {
    this.sourceDbService.getSourceDb(Number(this.dbId)).subscribe(response => { this.sourceDb = response })
  }

  openSnackBar(message: string, action: string) {
    this.snackBar.open(message, action , {
      duration: 5000
    });
  }

  onSubmit() {
    console.log('saving config')
    this.configForm.get('is_configured')?.setValue(true);
    this.configEditorService.createConfigEditorsingleInstance(this.configForm.value, Number(this.dbId))
      .subscribe(() => {
        this.openSnackBar('Configuration saved successfully', 'OK');
      })
  }

}
