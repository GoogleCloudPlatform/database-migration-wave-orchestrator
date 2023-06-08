import { Component, OnInit } from '@angular/core';
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

  constructor(
    private configEditorService: ConfigEditorService,
    private sourceDbService: SourceDbService,
    private activatedRoute: ActivatedRoute,
  ) { }

  ngOnInit(): void {
    this.activatedRoute.queryParams.subscribe((params) => {
      this.dbId=params.databaseId;
      this.loadDb()
    })
  }

  loadDb() {
    this.sourceDbService.getSourceDb(Number(this.dbId)).subscribe(response => { this.sourceDb = response })
  }

  saveConfig() {
    console.log('saving config')
    this.configEditorService.createConfigEditorsingleInstance(this.config, Number(this.dbId)).subscribe((response) => console.log(response))
  }

}
