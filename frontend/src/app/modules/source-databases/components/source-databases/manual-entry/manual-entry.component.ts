import { Component, OnInit } from '@angular/core';
import {Router} from "@angular/router";
import {MatSnackBar} from "@angular/material/snack-bar";
import {SourceDbService} from "@app-services/source-db/source-db.service";
import {FormControl, FormGroup} from "@angular/forms";
import {UtilService} from "@app-services/util/util.service";

@Component({
  selector: 'app-manual-entry',
  templateUrl: './manual-entry.component.html',
  styleUrls: ['./manual-entry.component.scss']
})
export class ManualEntryComponent implements OnInit {

  currentProjectId!: number;
  db_engines = {
    "POSTGRES": "Postgres",
    "MYSQL": "MySQL"
  }

  form = new FormGroup({
    "server": new FormControl(""),
    "db_engine": new FormControl(""),
    "db_name": new FormControl(""),
  })

  constructor(
    private sourceDbService: SourceDbService,
    private utilService: UtilService,
    private router: Router,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    if (this.utilService.getCurrentProjectId() != null) {
      this.currentProjectId = this.utilService.getCurrentProjectId();
    }
  }

  addSourceDatabase() {
    this.sourceDbService.saveSourceDb({
      project_id: this.currentProjectId,
      server: this.form.get("server")?.value as string,
      db_name: this.form.get("db_name")?.value as string,
      db_engine: this.form.get("db_engine")?.value as string,
      db_type: undefined,
    }).subscribe(() => {
      this.openSnackBar("Database saved successfully")
    })
  }

  goBack() {
    this.router.navigateByUrl('sourcedatabases')
  }

  openSnackBar(message:string) {
    this.snackBar.open(message, 'Accept' , {
      duration: 5000,
    }).afterDismissed().subscribe(() => this.goBack());
  }

}
