/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

export interface Target {
  luns: {
    storage_volume: string;
    size_gb: string;
    lun_name: string;
  }[],
  data: Target[];
  id?: number;
  client_ip?: string,
  cpu?: string,
  name?: string,
  ram?: string | number,
  secret_name?: string | null;
  socket?: string,
  isMapped?: boolean;
  created_at?: string;
  location?: string;
}
