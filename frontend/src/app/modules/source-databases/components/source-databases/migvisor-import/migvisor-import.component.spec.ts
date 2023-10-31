import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MigvisorImportComponent } from './migvisor-import.component';

describe('MigvisorImportComponent', () => {
  let component: MigvisorImportComponent;
  let fixture: ComponentFixture<MigvisorImportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MigvisorImportComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MigvisorImportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
