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
import datetime

import pytest
from dateutil.tz import tzutc
from ddf import G

from apigateway.apps.esb.bkcore.models import ComponentReleaseHistory, ComponentSystem, ESBChannel
from apigateway.apps.esb.component import views
from apigateway.apps.esb.component.constants import ESB_RELEASE_TASK_EXPIRES
from apigateway.apps.esb.constants import DataTypeEnum
from apigateway.core.models import Gateway
from apigateway.tests.utils.testing import get_response_json

pytestmark = pytest.mark.django_db(transaction=True, databases=["default", "bkcore"])


class TestESBChannelViewSet:
    @pytest.fixture(autouse=True)
    def setup_fixture(self, request_factory):
        self.factory = request_factory

    def test_list(self):
        G(ESBChannel)

        request = self.factory.get("/")

        view = views.ESBChannelViewSet.as_view({"get": "list"})
        response = view(request)
        result = get_response_json(response)

        assert response.status_code == 200
        assert len(result["data"]) >= 1

    def test_retrieve(self):
        channel = G(ESBChannel)

        request = self.factory.get("/")

        view = views.ESBChannelViewSet.as_view({"get": "retrieve"})
        response = view(request, id=channel.id)
        result = get_response_json(response)

        assert response.status_code == 200
        assert result["data"]["id"] == channel.id

    def test_create(self):
        system = G(ComponentSystem, board="test")
        view = views.ESBChannelViewSet.as_view({"post": "create"})

        request = self.factory.post(
            "/",
            data={
                "system_id": system.id,
                "description": "test",
                "name": "echo",
                "method": "",
                "path": "/echo/create",
                "component_codename": "generic.test.echo_create",
                "permission_level": "normal",
                "timeout": 30,
                "is_active": False,
                "config": {"name": "test"},
            },
        )
        response = view(request)
        result = get_response_json(response)
        channel = ESBChannel.objects.get(id=result["data"]["id"])

        assert response.status_code == 200
        assert channel.board == "test"
        assert channel.data_type == 3
        assert channel.is_active is False
        assert channel.is_public is True
        assert channel.config == {}

    def test_update(self):
        system = G(ComponentSystem)
        channel = G(ESBChannel, system=system)
        view = views.ESBChannelViewSet.as_view({"put": "update"})

        request = self.factory.put(
            "/",
            data={
                "system_id": system.id,
                "name": "echo",
                "description": "test",
                "method": "",
                "path": "/echo/update",
                "component_codename": "generic.test.echo_update",
                "permission_level": "normal",
                "timeout": 60,
                "is_active": False,
                "config": {"name": "test"},
            },
        )
        response = view(request, id=channel.id)
        get_response_json(response)
        channel = ESBChannel.objects.get(id=channel.id)

        assert response.status_code == 200
        assert channel.timeout == 60
        assert channel.permission_level == "normal"

    def test_delete(self):
        system = G(ComponentSystem)
        view = views.ESBChannelViewSet.as_view({"delete": "destroy"})

        channel = G(ESBChannel, system=system, data_type=DataTypeEnum.CUSTOM.value)
        request = self.factory.delete("/")
        response = view(request, id=channel.id)
        get_response_json(response)

        assert response.status_code == 200
        assert not ESBChannel.objects.filter(id=channel.id).exists()

        # channel is official
        channel = G(ESBChannel, system=system, data_type=DataTypeEnum.OFFICIAL_PUBLIC.value)
        request = self.factory.delete("/")
        response = view(request, id=channel.id)

        assert response.status_code == 400
        assert ESBChannel.objects.filter(id=channel.id).exists()


class TestESBChannelBatchViewSet:
    @pytest.fixture(autouse=True)
    def setup_fixture(self, request_factory):
        self.factory = request_factory

    def test_destroy(self):
        system = G(ComponentSystem)
        view = views.ESBChannelBatchViewSet.as_view({"delete": "destroy"})

        channel = G(ESBChannel, system=system, data_type=DataTypeEnum.CUSTOM.value)
        request = self.factory.delete("/", data={"ids": [channel.id]})
        response = view(request)
        get_response_json(response)

        assert response.status_code == 200
        assert not ESBChannel.objects.filter(id=channel.id).exists()

        # channel is official
        channel = G(ESBChannel, system=system, data_type=DataTypeEnum.OFFICIAL_PUBLIC.value)
        request = self.factory.delete("/", data={"ids": [channel.id]})
        response = view(request)

        assert response.status_code == 400
        assert ESBChannel.objects.filter(id=channel.id).exists()


class TestComponentSyncViewSet:
    @pytest.fixture(autouse=True)
    def setup_fixtures(self, request_factory):
        self.factory = request_factory

    @pytest.mark.parametrize(
        "locked, expected",
        [
            (True, {"is_releasing": True}),
            (False, {"is_releasing": False}),
        ],
    )
    def test_get_release_status(self, mocker, locked, expected, fake_admin_user):
        view = views.ComponentSyncViewSet.as_view({"get": "get_release_status"})
        request = self.factory.get("/sync/release/status/")
        request.user = fake_admin_user

        # locked
        mocker.patch(
            "apigateway.apps.esb.component.views.get_release_lock",
            return_value=mocker.MagicMock(**{"locked.return_value": locked}),
        )
        response = view(request)
        result = get_response_json(response)
        assert result["code"] == 0
        assert result["data"] == expected

    @pytest.mark.parametrize(
        "importing_resources, unspecified_resources, expected",
        [
            (
                [
                    {
                        "id": 1,
                        "method": "GET",
                        "path": "/echo/1/",
                        "name": "get_echo_1",
                        "extend_data": {
                            "system_name": "DEMO",
                            "component_id": 100,
                            "component_name": "echo_1",
                            "component_method": "GET",
                            "component_path": "/echo/1/",
                            "component_permission_level": "unlimited",
                        },
                    }
                ],
                [
                    {
                        "id": 2,
                        "method": "POST",
                        "path": "/echo/2/",
                        "name": "post_echo_2",
                    }
                ],
                [
                    {
                        "resource_id": 2,
                        "resource_name": "post_echo_2",
                    },
                    {
                        "resource_id": 1,
                        "resource_name": "get_echo_1",
                        "system_name": "DEMO",
                        "component_id": 100,
                        "component_name": "echo_1",
                        "component_method": "GET",
                        "component_path": "/echo/1/",
                        "component_permission_level": "unlimited",
                    },
                ],
            )
        ],
    )
    def test_sync_check(self, mocker, importing_resources, unspecified_resources, expected, fake_admin_user):
        mocker.patch(
            "apigateway.apps.esb.component.views.ComponentSyncViewSet._get_esb_gateway", return_value=G(Gateway)
        )
        mocker.patch(
            "apigateway.apps.esb.component.views.ComponentSynchronizer.get_importing_resources",
            return_value=importing_resources,
        )
        mock_set_imported_resources = mocker.patch(
            "apigateway.apps.esb.component.views.ResourcesImporter.set_importing_resources"
        )
        mocker.patch(
            "apigateway.apps.esb.component.views.ResourcesImporter.get_unspecified_resources",
            return_value=unspecified_resources,
        )

        view = views.ComponentSyncViewSet.as_view({"get": "sync_check"})
        request = self.factory.get("/sync/check/")
        request.user = fake_admin_user
        response = view(request)
        result = get_response_json(response)

        assert response.status_code == 200, result
        assert result["data"] == expected
        mock_set_imported_resources.assert_called_once_with(importing_resources)

    def test_sync_and_release(self, mocker, faker, fake_admin_user):
        api_id = faker.pyint()
        mock_api = mocker.MagicMock(id=api_id)

        mocker.patch(
            "apigateway.apps.esb.component.views.ComponentSyncViewSet._get_esb_gateway", return_value=mock_api
        )
        mock_sync_and_release = mocker.patch(
            "apigateway.apps.esb.component.views.sync_and_release_esb_components.apply_async"
        )

        view = views.ComponentSyncViewSet.as_view({"post": "sync_and_release"})
        request = self.factory.post("/sync/release/")
        request.user = fake_admin_user

        # locked
        mocker.patch(
            "apigateway.apps.esb.component.views.get_release_lock",
            return_value=mocker.MagicMock(**{"locked.return_value": True}),
        )
        response = view(request)
        result = get_response_json(response)
        assert result["code"] != 0
        assert result["data"] == {"is_releasing": True}
        mock_sync_and_release.assert_not_called()

        # not locked
        mocker.patch(
            "apigateway.apps.esb.component.views.get_release_lock",
            return_value=mocker.MagicMock(**{"locked.return_value": False}),
        )
        response = view(request)
        result = get_response_json(response)
        assert result["code"] == 0
        assert result["data"] == {"is_releasing": True}
        mock_sync_and_release.assert_called_once_with(
            args=(api_id, "admin", request.user.token.access_token, False),
            expires=ESB_RELEASE_TASK_EXPIRES,
            ignore_result=True,
        )


class TestComponentReleaseHistoryViewSet:
    @pytest.fixture(autouse=True)
    def setup_fixtures(self, request_factory):
        self.factory = request_factory

    @pytest.mark.parametrize(
        "histories, resource_version_ids, resource_version_id_to_fields, expected",
        [
            (
                [
                    {
                        "id": 1,
                        "resource_version_id": 1,
                        "data": [],
                        "comment": "test",
                        "status": "success",
                        "message": "ok",
                        "created_time": datetime.datetime(2020, 12, 13, 15, 4, 0, tzinfo=tzutc()),
                        "created_by": "admin",
                    }
                ],
                [1],
                {
                    1: {
                        "name": "bk-esb-demo",
                        "title": "v1",
                        "version": "1.0.0",
                    },
                },
                [
                    {
                        "id": 1,
                        "created_time": "2020-12-13 23:04:00",
                        "resource_version_name": "bk-esb-demo",
                        "resource_version_title": "v1",
                        "resource_version_display": "1.0.0(v1)",
                        "created_by": "admin",
                        "status": "success",
                        "message": "ok",
                    }
                ],
            )
        ],
    )
    def test_list(self, mocker, histories, resource_version_ids, resource_version_id_to_fields, expected):
        mock_get_histories = mocker.patch(
            "apigateway.apps.esb.component.views.ComponentReleaseHistory.objects.get_histories", return_value=histories
        )
        mock_resource_version_get_id_to_fields = mocker.patch(
            "apigateway.apps.esb.component.views.ResourceVersion.objects.get_id_to_fields_map",
            return_value=resource_version_id_to_fields,
        )

        request = self.factory.get(
            "/sync/release/histories/",
            data={
                "time_start": 1639379302,
                "time_end": 1639379310,
            },
        )

        view = views.ComponentReleaseHistoryViewSet.as_view({"get": "list"})
        response = view(request)

        result = get_response_json(response)
        assert result["code"] == 0
        assert result["data"]["results"] == expected, result

        mock_get_histories.assert_called_once_with(
            time_start=datetime.datetime(2021, 12, 13, 7, 8, 22, tzinfo=tzutc()),
            time_end=datetime.datetime(2021, 12, 13, 7, 8, 30, tzinfo=tzutc()),
            order_by="-id",
        )
        mock_resource_version_get_id_to_fields.assert_called_once_with(resource_version_ids=resource_version_ids)

    def test_retrieve(self):
        history = G(
            ComponentReleaseHistory,
            data=[
                {
                    "id": 1,
                    "name": "echo",
                    "extend_data": {
                        "system_name": "DEMO",
                        "component_id": 1,
                        "component_name": "get_echo",
                        "component_method": "GET",
                        "component_path": "/echo/",
                        "component_permission_level": "unlimited",
                    },
                }
            ],
        )

        request = self.factory.get(f"/sync/release/histories/{history.id}/")

        view = views.ComponentReleaseHistoryViewSet.as_view({"get": "retrieve"})
        response = view(request, id=history.id)

        result = get_response_json(response)
        assert result["code"] == 0
        assert result["data"] == [
            {
                "resource_id": 1,
                "resource_name": "echo",
                "system_name": "DEMO",
                "component_id": 1,
                "component_name": "get_echo",
                "component_method": "GET",
                "component_path": "/echo/",
                "component_permission_level": "unlimited",
            }
        ]
