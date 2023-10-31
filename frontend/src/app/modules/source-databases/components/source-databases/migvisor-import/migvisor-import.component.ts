import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { SourceDbService } from '@app-services/source-db/source-db.service';
import { UtilService } from '@app-services/util/util.service';

@Component({
  selector: 'app-migvisor-import',
  templateUrl: './migvisor-import.component.html',
  styleUrls: ['./migvisor-import.component.scss']
})
export class MigvisorImportComponent implements OnInit {

  @ViewChild("fileUpload", {static: false}) fileUpload!: ElementRef;
  currentProjectId!: number;
  overrideDatabase: boolean = false;

  constructor(
    private sourceDbService: SourceDbService,
    private utilService: UtilService,
    private snackBar: MatSnackBar,
    private router: Router,
  ) { }

  ngOnInit(): void {
    if (this.utilService.getCurrentProjectId() != null) {
      this.currentProjectId = this.utilService.getCurrentProjectId();
    }
  }

  uploadFile() {
    const fileUpload = this.fileUpload.nativeElement;
    fileUpload.click();
    const formData = new FormData();
    fileUpload.onchange = () => {
      formData.append("file", fileUpload.files[0], fileUpload.files[0].name);
      formData.append("project_id", String(this.currentProjectId));
      formData.append("overwrite", String(this.overrideDatabase));
      this.sourceDbService.uploadSourceDbFile(formData).subscribe( resp => {
        if (!resp)
          return;
        this.openSnackBar('File uploaded successfully. ' + this.getResult(resp));
        fileUpload.value = null;
      },
      (error) => {
        this.openSnackBar(error);
        fileUpload.value = null;
      })
    };
  }

  getResult(resp: {added: number, skipped: number, updated: number}): string {
    return this.overrideDatabase
    ? `${resp.added} of new records and ${resp.updated} of overwritten`
    : `${resp.added} of new records and ${resp.skipped} of ignored`
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
