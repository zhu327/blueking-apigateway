# -*- coding: utf-8 -*-
#
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - API 网关(BlueKing - APIGateway) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
#
import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from apigateway.apps.stage.serializers import StageSLZ
from apigateway.core.models import Gateway, Stage
from apigateway.utils.django import get_object_or_None

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """新增环境

    如果环境不存在，则创建环境
    如果环境已存在，则跳过
    """

    def add_arguments(self, parser):
        parser.add_argument("--api", dest="api_name", required=True, help="gateway name")
        parser.add_argument("--name", type=str, dest="name", required=True)

    @transaction.atomic
    def handle(self, api_name: str, name: str, **options):
        gateway = Gateway.objects.get(name=api_name)
        stage = get_object_or_None(Stage, api=gateway, name=name)

        if stage:
            print(f"Stage [name={name}] exists and ignore")
            return

        # FIXME: 去除对 SLZ 的依赖, 应该直接构造 django model 然后save
        slz = StageSLZ(
            data={
                "name": name,
                "proxy_http": {
                    "timeout": 60,
                    "upstreams": {
                        "loadbalance": "roundrobin",
                        "hosts": [
                            {
                                "host": "http://0.0.0.1",
                                "weight": 100,
                            }
                        ],
                    },
                    "transform_headers": {
                        "set": {},
                        "delete": [],
                    },
                },
            },
            context={
                "api": gateway,
            },
        )

        slz.is_valid(raise_exception=True)
        slz.save(created_by="admin", updated_by="admin")

        logger.info(f"Add stage [name={name}] success")
